"""Refactor-tolerant observations for Runtime Entry Resolution v0.3 tests.

The profiler never raises from inside pytest instrumentation.  It records the
semantic boundary reached by the candidate and lets the test assert after the
candidate returns.  Byte snapshots independently expose persistent writes.
"""

from __future__ import annotations

import builtins
import importlib
import subprocess
import sys
from collections.abc import Callable, Iterable
from dataclasses import fields, is_dataclass
from pathlib import Path
from types import FrameType, ModuleType
from typing import Any, cast

_POPEN_INIT = cast(Callable[..., object], subprocess.Popen.__init__)
_POPEN_EXECUTE_CHILD = cast(
    Callable[..., object], vars(subprocess.Popen)["_execute_child"]
)

FORBIDDEN_MODULE_PREFIXES = (
    "argus.runtime.runtime_identity",
    "argus.runtime.runtime_config",
    "argus.runtime.environment_binding",
    "argus.runtime.data_root_marker_store",
)
_PUBLIC_BOUNDARY_NAMES = (
    "parse_runtime_identity", "load_runtime_identity", "resolve_runtime_identity",
    "parse_runtime_config", "load_runtime_config", "resolve_runtime_config",
    "verify_environment_binding", "bind_environment", "load_data_root_marker",
    "initialize_data_root_marker", "write_data_root_marker",
    "create_result_manifest", "write_result_manifest",
)


def _default_forbidden_callables() -> tuple[Callable[..., object], ...]:
    """Resolve public semantic destinations without touching Product privates."""

    destinations: list[Callable[..., object]] = [
        importlib.import_module, builtins.__import__, builtins.compile,
        builtins.exec, builtins.eval, _POPEN_INIT, _POPEN_EXECUTE_CHILD, subprocess.run,
    ]
    for module_name in FORBIDDEN_MODULE_PREFIXES:
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            continue
        for name in _PUBLIC_BOUNDARY_NAMES:
            value = getattr(module, name, None)
            if callable(value):
                destinations.append(value)
    return tuple(destinations)


def process_launch_callables() -> tuple[Callable[..., object], ...]:
    """Return stable executable process boundaries, including from-import Popen."""

    return (_POPEN_INIT, _POPEN_EXECUTE_CHILD, subprocess.run)


def observe_calls(
    operation: Callable[[], object],
    *,
    forbidden_callables: Iterable[Callable[..., object]] | None = None,
) -> tuple[object, tuple[str, ...]]:
    """Run *operation* and return its result plus forbidden semantic calls.

    The callback only appends strings.  In particular it never raises, so a
    violation becomes a deterministic assertion rather than pytest INTERNALERROR.
    """

    events: list[str] = []
    destinations = tuple(forbidden_callables or _default_forbidden_callables())
    python_codes = {
        value.__code__: f"{value.__module__}.{value.__qualname__}"
        for value in destinations
        if hasattr(value, "__code__")
    }
    c_destinations = {id(value): f"{value.__module__}.{value.__qualname__}" for value in destinations}

    def profiler(frame: FrameType, event: str, arg: Any) -> None:
        if event == "call" and frame.f_code in python_codes:
            events.append(python_codes[frame.f_code])
        elif event == "c_call" and id(arg) in c_destinations:
            events.append(c_destinations[id(arg)])

    previous = sys.getprofile()
    sys.setprofile(profiler)
    try:
        result = operation()
    finally:
        sys.setprofile(previous)
    return result, tuple(events)


def observe_call_attempt(
    operation: Callable[[], object],
    *,
    forbidden_callables: Iterable[Callable[..., object]] | None = None,
) -> tuple[object | None, BaseException | None, tuple[str, ...]]:
    """Observe an operation whose Product/spy behavior may raise normally."""

    def guarded() -> object:
        try:
            return operation()
        except Exception as error:  # noqa: BLE001 - report Product/spy failures unchanged
            return error

    value, events = observe_calls(guarded, forbidden_callables=forbidden_callables)
    if isinstance(value, BaseException):
        return None, value, events
    return value, None, events


def byte_snapshot(paths: Iterable[Path]) -> dict[Path, bytes | None]:
    return {path: path.read_bytes() if path.is_file() else None for path in paths}


def directory_snapshot(root: Path) -> dict[str, tuple[str, bytes | None]]:
    """Snapshot every entry below *root* without assuming a marker filename."""

    if not root.exists():
        return {".": ("absent", None)}
    snapshot: dict[str, tuple[str, bytes | None]] = {".": ("directory", None)}
    for path in sorted(root.rglob("*"), key=lambda value: value.as_posix()):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            snapshot[relative] = ("symlink", str(path.readlink()).encode())
        elif path.is_file():
            snapshot[relative] = ("file", path.read_bytes())
        elif path.is_dir():
            snapshot[relative] = ("directory", None)
        else:
            snapshot[relative] = ("other", None)
    return snapshot


def observe_path_exists(
    operation: Callable[[], object],
) -> tuple[object | None, BaseException | None, tuple[Path, ...]]:
    """Record ``Path.exists`` calls while preserving its normal behavior.

    The global method is restored before callers assert, so pytest's own path
    handling can never enter this observer while formatting a failure.
    """

    original = Path.exists
    calls: list[Path] = []

    def recording_exists(self: Path, *, follow_symlinks: bool = True) -> bool:
        calls.append(self)
        return original(self, follow_symlinks=follow_symlinks)

    Path.exists = recording_exists
    try:
        try:
            result = operation()
        except Exception as error:  # noqa: BLE001 - return Product failure as data
            return None, error, tuple(calls)
        return result, None, tuple(calls)
    finally:
        Path.exists = original


def public_type_contract_violations(module: ModuleType) -> tuple[str, ...]:
    expected = {
        "RuntimeEntryResolutionDiagnostic": ("code", "field_name"),
        "RuntimeEntryResolutionFailure": ("diagnostic",),
        "ResolvedPythonModuleTarget": ("kind", "module_name", "origin_path"),
        "RuntimeEntryResolutionResult": (
            "startup_target",
            "expected_binding",
            "data_root_locator",
        ),
    }
    violations: list[str] = []
    for name, field_names in expected.items():
        value = vars(module).get(name)
        if not isinstance(value, type) or not is_dataclass(value):
            violations.append(f"{name}:not-dataclass")
            continue
        parameters = getattr(value, "__dataclass_params__", None)
        if not bool(getattr(parameters, "frozen", False)):
            violations.append(f"{name}:not-frozen")
        if tuple(field.name for field in fields(value)) != field_names:
            violations.append(f"{name}:fields")
        if value.__module__ != module.__name__:
            violations.append(f"{name}:non-local")
    return tuple(violations)
