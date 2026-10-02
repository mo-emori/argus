from __future__ import annotations

import ast
import builtins
import importlib
import importlib.util
import inspect
import os
import socket
import subprocess
import time
from collections.abc import Callable
from dataclasses import FrozenInstanceError
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import cast

import pytest

import argus.runtime.runtime_config as runtime_config_module
import argus.runtime.runtime_identity as runtime_identity_module
from argus.runtime.data_root_locator import DataRootLocator
from argus.runtime.environment import Environment
from argus.runtime.runtime_config import (
    RuntimeConfigSnapshot,
    RuntimeConfigState,
    parse_runtime_config,
)
from argus.runtime.runtime_identity import RuntimeIdentity, parse_runtime_identity

from ._candidate import (
    MODULE_NAME,
    PUBLIC_SYMBOLS,
    VALID_MANIFEST,
    assert_closed_dataclass,
    assert_failure,
    forbidden,
    identity,
    invoke,
    json_bytes,
    manifest,
    resolver,
    snapshot,
    surface,
)
from ._semantic_boundaries import semantic_boundary_findings
from ._semantic_observer import (
    byte_snapshot,
    directory_snapshot,
    observe_calls,
    observe_path_exists,
    process_launch_callables,
    public_type_contract_violations,
)

TEST_STRATEGY = Path("docs/test/argus_runtime_entry_resolution_test_strategy_v0.1.md")
CONTRACT = Path("docs/contracts/argus_runtime_entry_resolution_contract_v0.1.md")
REGISTRY = Path("docs/development/argus_capability_registry.md")


def _failure(tmp_path: Path, data: bytes, code: str, field: str | None) -> None:
    module, result = invoke(tmp_path, data)
    assert_failure(result, module, code, field)


def _finder(value: object) -> Callable[[str], object]:
    def find(_name: str) -> object:
        return value

    return find


def _controlled_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, data: bytes = VALID_MANIFEST
) -> tuple[ModuleType, object, Path]:
    origin = (tmp_path / "controlled-package" / "__init__.py").absolute()
    origin.parent.mkdir(exist_ok=True)
    origin.write_bytes(b"controlled-origin")
    monkeypatch.setattr(
        importlib.util,
        "find_spec",
        _finder(
            SimpleNamespace(origin=str(origin), submodule_search_locations=[str(origin.parent)])
        ),
    )
    module, result = invoke(tmp_path, data)
    return module, result, origin


def _assert_exact_success(module: object, result: object, origin: Path, tmp_path: Path) -> None:
    module_dict = vars(module)
    assert type(result) is module_dict["RuntimeEntryResolutionResult"]
    assert vars(vars(result)["startup_target"]) == {
        "kind": "python_module",
        "module_name": "argus.runtime",
        "origin_path": origin,
    }
    upstream = identity()
    assert vars(vars(result)["expected_binding"]) == {
        "state_id": upstream.state_id,
        "data_root_id": upstream.data_root_id,
        "environment": upstream.environment,
    }
    assert vars(vars(result)["data_root_locator"]) == {
        "path": (tmp_path / "sentinel-data-root").absolute()
    }


# RER-U-001
def test_rer_u_001_canonical_manifest_reaches_target_resolution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module, result, origin = _controlled_success(tmp_path, monkeypatch)
    _assert_exact_success(module, result, origin, tmp_path)


# RER-U-002
def test_rer_u_002_utf8_bom_is_manifest_read_error(tmp_path: Path) -> None:
    _failure(tmp_path, b"\xef\xbb\xbf" + VALID_MANIFEST, "MANIFEST_READ_ERROR", None)


# RER-U-003
@pytest.mark.parametrize(
    "data",
    [b'{"schema_version":', VALID_MANIFEST + b" true", (b"[" * 3000) + (b"]" * 3000)],
    ids=["truncated", "trailing-token", "bounded-deep-input"],
)
def test_rer_u_003_malformed_json_is_typed(tmp_path: Path, data: bytes) -> None:
    _failure(tmp_path, data, "MALFORMED_JSON", None)


# RER-U-004
@pytest.mark.parametrize(
    "data",
    [
        b'{"schema_version":"0.1","schema_version":"0.1","startup":{}}',
        b'{"schema_version":"0.1","schema\\u005fversion":"0.1","startup":{}}',
    ],
    ids=["equal-values", "decoded-name"],
)
def test_rer_u_004_root_duplicates_are_rejected(tmp_path: Path, data: bytes) -> None:
    _failure(tmp_path, data, "DUPLICATE_FIELD", "schema_version")


# RER-U-005
def test_rer_u_005_startup_duplicates_are_rejected(tmp_path: Path) -> None:
    data = b'{"schema_version":"0.1","startup":{"kind":"python_module","kind":"python_module","entry":"argus.runtime"}}'
    _failure(tmp_path, data, "DUPLICATE_FIELD", "kind")


# RER-U-006
def test_rer_u_006_unknown_nested_duplicates_precede_ignore(tmp_path: Path) -> None:
    data = b'{"schema_version":"0.1","startup":{"kind":"python_module","entry":"argus.runtime"},"future":{"x":1,"x":1}}'
    _failure(tmp_path, data, "DUPLICATE_FIELD", "x")


# RER-U-007
@pytest.mark.parametrize("data", [b"[]", b'"x"', b"1", b"true", b"null"])
def test_rer_u_007_root_must_be_object(tmp_path: Path, data: bytes) -> None:
    _failure(tmp_path, data, "MANIFEST_SCHEMA_INVALID", None)


# RER-U-008
def test_rer_u_008_schema_version_is_required(tmp_path: Path) -> None:
    _failure(tmp_path, b'{"startup":{}}', "MANIFEST_SCHEMA_INVALID", "schema_version")


# RER-U-009
@pytest.mark.parametrize("value", [1, None, True, [], {}])
def test_rer_u_009_schema_version_requires_string(tmp_path: Path, value: object) -> None:
    _failure(
        tmp_path,
        json_bytes({"schema_version": value, "startup": {}}),
        "MANIFEST_SCHEMA_INVALID",
        "schema_version",
    )


# RER-U-010
@pytest.mark.parametrize("value", ["0.0", "0.1.0", "1", "", " 0.1", "０.１"])
def test_rer_u_010_schema_version_is_exact(tmp_path: Path, value: str) -> None:
    _failure(
        tmp_path,
        json_bytes({"schema_version": value, "startup": {}}),
        "UNSUPPORTED_SCHEMA_VERSION",
        "schema_version",
    )


# RER-U-011
@pytest.mark.parametrize(
    "startup,include",
    [(None, False), (None, True), (1, True), ("x", True), ([], True)],
    ids=["missing", "json-null", "number", "string", "array"],
)
def test_rer_u_011_startup_requires_object(tmp_path: Path, startup: object, include: bool) -> None:
    document: dict[str, object] = {"schema_version": "0.1"}
    if include:
        document["startup"] = startup
    _failure(tmp_path, json_bytes(document), "MANIFEST_SCHEMA_INVALID", "startup")


# RER-U-012
@pytest.mark.parametrize(
    "value,include",
    [(None, False), (None, True), (1, True), (True, True), ([], True), ({}, True)],
    ids=["missing", "json-null", "number", "boolean", "array", "object"],
)
def test_rer_u_012_startup_kind_requires_string(
    tmp_path: Path, value: object, include: bool
) -> None:
    startup: dict[str, object] = {"entry": "argus.runtime"}
    if include:
        startup["kind"] = value
    _failure(
        tmp_path,
        json_bytes({"schema_version": "0.1", "startup": startup}),
        "MANIFEST_SCHEMA_INVALID",
        "startup.kind",
    )


# RER-U-013
@pytest.mark.parametrize(
    "value", ["Python_Module", " python_module", "python-module", "ｐython_module", "executable"]
)
def test_rer_u_013_startup_kind_is_closed_exact_token(tmp_path: Path, value: str) -> None:
    data = json_bytes(
        {"schema_version": "0.1", "startup": {"kind": value, "entry": "argus.runtime"}}
    )
    _failure(tmp_path, data, "MANIFEST_SCHEMA_INVALID", "startup.kind")


# RER-U-014
@pytest.mark.parametrize(
    "value,include",
    [(None, False), (None, True), (1, True), (True, True), ([], True), ({}, True)],
    ids=["missing", "json-null", "number", "boolean", "array", "object"],
)
def test_rer_u_014_startup_entry_requires_string(
    tmp_path: Path, value: object, include: bool
) -> None:
    startup: dict[str, object] = {"kind": "python_module"}
    if include:
        startup["entry"] = value
    _failure(
        tmp_path,
        json_bytes({"schema_version": "0.1", "startup": startup}),
        "MANIFEST_SCHEMA_INVALID",
        "startup.entry",
    )


# RER-U-015
@pytest.mark.parametrize(
    "value",
    [
        "argus/runtime",
        "argus.runtime:main",
        ".argus.runtime",
        "argus.runtime.__main__",
        " Argus.Runtime",
        "argus．runtime",
    ],
)
def test_rer_u_015_startup_entry_is_exact_module(tmp_path: Path, value: str) -> None:
    data = json_bytes(
        {"schema_version": "0.1", "startup": {"kind": "python_module", "entry": value}}
    )
    _failure(tmp_path, data, "MANIFEST_SCHEMA_INVALID", "startup.entry")


# RER-U-016
def test_rer_u_016_unknown_root_members_are_inert(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module, base, origin = _controlled_success(tmp_path, monkeypatch)
    _assert_exact_success(module, base, origin, tmp_path)
    extended = _controlled_success(
        tmp_path,
        monkeypatch,
        json_bytes(
            {
                "future": [1, {"x": True}],
                "schema_version": "0.1",
                "startup": {"kind": "python_module", "entry": "argus.runtime"},
            }
        ),
    )[1]
    assert extended == base


# RER-U-017
def test_rer_u_017_unknown_startup_members_are_inert(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module, base, origin = _controlled_success(tmp_path, monkeypatch)
    _assert_exact_success(module, base, origin, tmp_path)
    data = json_bytes(
        {
            "schema_version": "0.1",
            "startup": {"future": {"x": 1}, "entry": "argus.runtime", "kind": "python_module"},
        }
    )
    assert _controlled_success(tmp_path, monkeypatch, data)[1] == base


# RER-U-018
def test_rer_u_018_unknown_fields_cannot_supply_alternates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data = json_bytes(
        {
            "schema_version": "0.1",
            "path": "evil",
            "binding": "evil",
            "fallback": "evil",
            "startup": {
                "kind": "python_module",
                "entry": "argus.runtime",
                "command": "evil",
                "candidates": ["evil"],
            },
        }
    )
    module, result, origin = _controlled_success(tmp_path, monkeypatch, data)
    _assert_exact_success(module, result, origin, tmp_path)


# RER-U-019
def test_rer_u_019_schema_defects_use_canonical_precedence(tmp_path: Path) -> None:
    data = json_bytes({"schema_version": 1, "startup": {"kind": 2, "entry": 3}})
    _failure(tmp_path, data, "MANIFEST_SCHEMA_INVALID", "schema_version")


# RER-U-020
def test_rer_u_020_whitespace_and_key_order_only_are_equivalent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module, first, origin = _controlled_success(tmp_path, monkeypatch)
    _assert_exact_success(module, first, origin, tmp_path)
    second = _controlled_success(
        tmp_path,
        monkeypatch,
        b' \n{"startup":{"entry":"argus.runtime","kind":"python_module"},"schema_version":"0.1"}\t',
    )[1]
    assert first == second


# RER-C-001
def test_rer_c_001_only_explicit_manifest_is_loaded_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = manifest(tmp_path)
    reads: list[Path] = []
    original = Path.read_bytes

    def counting_read(value: Path) -> bytes:
        reads.append(value)
        return original(value)

    monkeypatch.setattr(Path, "read_bytes", counting_read)
    resolver(surface())(identity(), snapshot(tmp_path), path)
    assert reads == [path]


# RER-C-002
def test_rer_c_002_relative_manifest_path_is_rejected(tmp_path: Path) -> None:
    module = surface()
    result = resolver(module)(identity(), snapshot(tmp_path), Path("manifest.json"))
    assert_failure(result, module, "MANIFEST_PATH_INVALID", None)


# RER-C-003
@pytest.mark.parametrize("name", ["Manifest.json", "other.json", "manifest.json/child"])
def test_rer_c_003_manifest_basename_is_exact(tmp_path: Path, name: str) -> None:
    module = surface()
    result = resolver(module)(identity(), snapshot(tmp_path), (tmp_path / name).absolute())
    assert_failure(result, module, "MANIFEST_PATH_INVALID", None)


# RER-C-004
def test_rer_c_004_lexical_path_failure_is_typed(tmp_path: Path) -> None:
    class BrokenPath(type(Path())):
        @property
        def name(self) -> str:
            raise OSError("sentinel")

    module = surface()
    result = resolver(module)(
        identity(), snapshot(tmp_path), BrokenPath(tmp_path / "manifest.json")
    )
    assert_failure(result, module, "MANIFEST_PATH_INVALID", None)


# RER-C-005
def test_rer_c_005_absent_manifest_is_not_found(tmp_path: Path) -> None:
    module = surface()
    result = resolver(module)(
        identity(), snapshot(tmp_path), (tmp_path / "manifest.json").absolute()
    )
    assert_failure(result, module, "MANIFEST_NOT_FOUND", None)


# RER-C-006
def test_rer_c_006_non_regular_manifest_is_read_error(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    path.mkdir()
    module = surface()
    assert_failure(
        resolver(module)(identity(), snapshot(tmp_path), path.absolute()),
        module,
        "MANIFEST_READ_ERROR",
        None,
    )


# RER-C-007
def test_rer_c_007_manifest_io_error_is_typed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = manifest(tmp_path)

    def fail_read(_path: Path) -> bytes:
        raise PermissionError("secret path")

    monkeypatch.setattr(Path, "read_bytes", fail_read)
    module = surface()
    result = resolver(module)(identity(), snapshot(tmp_path), path)
    assert_failure(result, module, "MANIFEST_READ_ERROR", None)
    assert "secret path" not in repr(result)


# RER-C-008
def test_rer_c_008_invalid_utf8_is_read_error(tmp_path: Path) -> None:
    _failure(tmp_path, b"\xff", "MANIFEST_READ_ERROR", None)


# RER-C-009
@pytest.mark.parametrize(
    "data,code,field",
    [(b"{", "MALFORMED_JSON", None), (b"{}", "MANIFEST_SCHEMA_INVALID", "schema_version")],
)
def test_rer_c_009_earliest_stage_is_terminal(
    tmp_path: Path, data: bytes, code: str, field: str | None
) -> None:
    _failure(tmp_path, data, code, field)


# RER-C-010
def test_rer_c_010_finder_receives_exact_module_without_import(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[str] = []

    def find_missing(name: str) -> None:
        calls.append(name)

    monkeypatch.setattr(importlib.util, "find_spec", find_missing)
    module, result = invoke(tmp_path)
    assert_failure(result, module, "STARTUP_TARGET_NOT_FOUND", "startup.entry")
    assert calls == ["argus.runtime"]


# RER-C-011
def test_rer_c_011_missing_spec_is_target_not_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def find_missing(_name: str) -> None:
        return None

    monkeypatch.setattr(importlib.util, "find_spec", find_missing)
    module, result = invoke(tmp_path)
    assert_failure(result, module, "STARTUP_TARGET_NOT_FOUND", "startup.entry")


# RER-C-012
def test_rer_c_012_finder_exception_is_target_invalid(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail_find(_name: str) -> None:
        raise ValueError("sentinel")

    monkeypatch.setattr(importlib.util, "find_spec", fail_find)
    module, result = invoke(tmp_path)
    assert_failure(result, module, "STARTUP_TARGET_INVALID", "startup.entry")


# RER-C-013
@pytest.mark.parametrize("origin", ["built-in", "frozen", None])
def test_rer_c_013_non_concrete_specs_are_invalid(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, origin: str | None
) -> None:
    monkeypatch.setattr(
        importlib.util,
        "find_spec",
        _finder(SimpleNamespace(origin=origin, submodule_search_locations=None)),
    )
    module, result = invoke(tmp_path)
    assert_failure(result, module, "STARTUP_TARGET_INVALID", "startup.entry")


# RER-C-014
def test_rer_c_014_non_package_module_is_invalid(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    origin = tmp_path / "module.py"
    origin.write_bytes(b"")
    monkeypatch.setattr(
        importlib.util,
        "find_spec",
        _finder(SimpleNamespace(origin=str(origin), submodule_search_locations=None)),
    )
    module, result = invoke(tmp_path)
    assert_failure(result, module, "STARTUP_TARGET_INVALID", "startup.entry")


# RER-C-015
def test_rer_c_015_multiple_package_locations_are_invalid(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    origin = tmp_path / "__init__.py"
    origin.write_bytes(b"")
    monkeypatch.setattr(
        importlib.util,
        "find_spec",
        _finder(
            SimpleNamespace(
                origin=str(origin),
                submodule_search_locations=[str(tmp_path), str(tmp_path / "other")],
            )
        ),
    )
    module, result = invoke(tmp_path)
    assert_failure(result, module, "STARTUP_TARGET_INVALID", "startup.entry")


# RER-C-016
def test_rer_c_016_absent_origin_is_target_not_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    origin = tmp_path / "missing" / "__init__.py"
    monkeypatch.setattr(
        importlib.util,
        "find_spec",
        _finder(
            SimpleNamespace(origin=str(origin), submodule_search_locations=[str(origin.parent)])
        ),
    )
    module, result = invoke(tmp_path)
    assert_failure(result, module, "STARTUP_TARGET_NOT_FOUND", "startup.entry")


# RER-C-017
def test_rer_c_017_origin_basename_must_be_init(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    origin = tmp_path / "runtime.py"
    origin.write_bytes(b"")
    monkeypatch.setattr(
        importlib.util,
        "find_spec",
        _finder(SimpleNamespace(origin=str(origin), submodule_search_locations=[str(tmp_path)])),
    )
    module, result = invoke(tmp_path)
    assert_failure(result, module, "STARTUP_TARGET_INVALID", "startup.entry")


# RER-C-018
def test_rer_c_018_origin_must_be_regular_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    origin = tmp_path / "__init__.py"
    origin.mkdir()
    monkeypatch.setattr(
        importlib.util,
        "find_spec",
        _finder(SimpleNamespace(origin=str(origin), submodule_search_locations=[str(tmp_path)])),
    )
    module, result = invoke(tmp_path)
    assert_failure(result, module, "STARTUP_TARGET_INVALID", "startup.entry")


# RER-C-019
def test_rer_c_019_unreadable_origin_is_invalid(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    origin = tmp_path / "pkg" / "__init__.py"
    origin.parent.mkdir()
    origin.write_bytes(b"")
    monkeypatch.setattr(
        importlib.util,
        "find_spec",
        _finder(
            SimpleNamespace(origin=str(origin), submodule_search_locations=[str(origin.parent)])
        ),
    )
    original = cast(Callable[..., object], Path.open)

    def guarded_open(value: Path, *args: object, **kwargs: object) -> object:
        if value == origin:
            raise PermissionError
        return original(value, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guarded_open)
    module, result = invoke(tmp_path)
    assert_failure(result, module, "STARTUP_TARGET_INVALID", "startup.entry")


# RER-C-020
def test_rer_c_020_valid_package_yields_exact_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    origin = tmp_path / "pkg" / "__init__.py"
    origin.parent.mkdir()
    origin.write_bytes(b"sentinel")
    monkeypatch.setattr(
        importlib.util,
        "find_spec",
        _finder(
            SimpleNamespace(origin=str(origin), submodule_search_locations=[str(origin.parent)])
        ),
    )
    _module, result = invoke(tmp_path)
    target = vars(result)["startup_target"]
    assert vars(target) == {
        "kind": "python_module",
        "module_name": "argus.runtime",
        "origin_path": origin.absolute(),
    }


# RER-C-021
def test_rer_c_021_resolution_has_no_prohibited_side_effects(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(subprocess, "run", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    before = VALID_MANIFEST
    invoke(tmp_path)
    assert VALID_MANIFEST == before


# RER-C-022
def test_rer_c_022_same_observations_are_deterministic_across_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = invoke(tmp_path)[1]
    other = tmp_path / "other"
    other.mkdir()
    monkeypatch.chdir(other)
    monkeypatch.setenv("ARGUS_ENV", "LIVE")
    assert invoke(tmp_path)[1] == first


# RER-C-023
def test_rer_c_023_success_result_has_exact_immutable_shape(tmp_path: Path) -> None:
    module, result = invoke(tmp_path)
    assert type(result) is module.__dict__["RuntimeEntryResolutionResult"]
    assert_closed_dataclass(result, ("startup_target", "expected_binding", "data_root_locator"))
    assert_closed_dataclass(vars(result)["startup_target"], ("kind", "module_name", "origin_path"))
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        result.__setattr__("extra", 1)


# RER-C-024
def test_rer_c_024_binding_inputs_map_only_from_upstream_values(tmp_path: Path) -> None:
    module = surface()
    upstream_identity = identity(Environment.PAPER)
    upstream_snapshot = snapshot(tmp_path, tmp_path / "sentinel-root")
    result = resolver(module)(upstream_identity, upstream_snapshot, manifest(tmp_path))
    assert vars(vars(result)["expected_binding"]) == {
        "state_id": upstream_identity.state_id,
        "data_root_id": upstream_identity.data_root_id,
        "environment": Environment.PAPER,
    }
    assert vars(vars(result)["data_root_locator"]) == {"path": upstream_snapshot.data_root_path}


# RER-C-025
def test_rer_c_025_data_root_locator_is_lexical_and_uninspected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    supplied = tmp_path / "missing" / "sentinel-root"
    original_exists = Path.exists
    original_is_file = Path.is_file
    original_resolve = cast(Callable[..., object], Path.resolve)
    original_open = cast(Callable[..., object], Path.open)

    def guard_exists(value: Path, *, follow_symlinks: bool = True) -> bool:
        if value == supplied:
            raise AssertionError("data_root_path must remain uninspected")
        return original_exists(value, follow_symlinks=follow_symlinks)

    def guard_is_file(value: Path, *, follow_symlinks: bool = True) -> bool:
        if value == supplied:
            raise AssertionError("data_root_path must remain uninspected")
        return original_is_file(value, follow_symlinks=follow_symlinks)

    def guard_resolve(value: Path, *args: object, **kwargs: object) -> object:
        if value == supplied:
            raise AssertionError("data_root_path must remain uncanonicalized")
        return original_resolve(value, *args, **kwargs)

    def guard_open(value: Path, *args: object, **kwargs: object) -> object:
        if value == supplied:
            raise AssertionError("data_root_path must not be read or written")
        return original_open(value, *args, **kwargs)

    monkeypatch.setattr(Path, "exists", guard_exists)
    monkeypatch.setattr(Path, "is_file", guard_is_file)
    monkeypatch.setattr(Path, "resolve", guard_resolve)
    monkeypatch.setattr(Path, "open", guard_open)
    module = surface()
    result = resolver(module)(identity(), snapshot(tmp_path, supplied), manifest(tmp_path))
    assert vars(vars(result)["data_root_locator"]) == {"path": supplied}


# RER-I-001
def test_rer_i_001_real_upstream_values_are_consumed_immutably(tmp_path: Path) -> None:
    identity_value = cast(
        RuntimeIdentity,
        parse_runtime_identity(
            b'{"schema_version":1,"state_id":"12345678-1234-4234-9234-123456789abc","data_root_id":"87654321-4321-4321-8321-cba987654321","environment":"TEST","created_at":"2026-10-01T00:00:00Z"}'
        ),
    )
    config = parse_runtime_config(b'{"config_version":1,"data_root":"sentinel"}')
    assert config.state is RuntimeConfigState.CONFIGURED
    config_snapshot = RuntimeConfigSnapshot(
        1, "sentinel", (tmp_path / "config.json").absolute(), (tmp_path / "sentinel").absolute()
    )
    module = surface()
    result = resolver(module)(identity_value, config_snapshot, manifest(tmp_path))
    assert vars(vars(result)["expected_binding"]) == {
        "state_id": identity_value.state_id,
        "data_root_id": identity_value.data_root_id,
        "environment": identity_value.environment,
    }
    assert vars(vars(result)["data_root_locator"]) == {"path": config_snapshot.data_root_path}


# RER-I-002
def test_rer_i_002_upstream_loaders_are_not_reinvoked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(runtime_identity_module, "parse_runtime_identity", forbidden)
    monkeypatch.setattr(runtime_config_module, "parse_runtime_config", forbidden)
    monkeypatch.setattr(runtime_config_module, "load_runtime_config", forbidden)
    invoke(tmp_path)


# RER-I-003
def test_rer_i_003_resolver_has_no_config_path_boundary(tmp_path: Path) -> None:
    signature = inspect.signature(resolver(surface()))
    assert tuple(signature.parameters) == (
        "identity",
        "config_snapshot",
        "artificial_manifest_path",
    )
    assert "config_path" not in signature.parameters


# RER-I-004
def test_rer_i_004_environment_is_never_inferred_from_paths(tmp_path: Path) -> None:
    live_path = tmp_path / "LIVE" / "manifest.json"
    live_path.parent.mkdir()
    live_path.write_bytes(VALID_MANIFEST)
    module = surface()
    result = resolver(module)(identity(Environment.TEST), snapshot(tmp_path), live_path.absolute())
    assert vars(vars(result)["expected_binding"])["environment"] is Environment.TEST


# RER-I-005
def test_rer_i_005_later_orchestrator_responsibilities_are_not_called(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = surface()
    del monkeypatch
    _, events = observe_calls(
        lambda: resolver(module)(identity(), snapshot(tmp_path), manifest(tmp_path))
    )
    assert events == ()


# RER-I-006
def test_rer_i_006_closed_upstream_public_contracts_remain_inherited() -> None:
    assert RuntimeIdentity.__module__ == "argus.runtime.runtime_identity"
    assert RuntimeConfigSnapshot.__module__ == "argus.runtime.runtime_config"
    assert DataRootLocator.__module__ == "argus.runtime.data_root_locator"
    assert Path("tests/unit/test_runtime_identity_contract.py").is_file()
    assert Path("tests/component/test_runtime_config_contract.py").is_file()


# RER-S-001
def test_rer_s_001_public_types_are_closed_local_immutable_shapes() -> None:
    module = surface()
    assert PUBLIC_SYMBOLS.issubset(module.__dict__)
    enum_type = module.__dict__["RuntimeEntryResolutionFailureCode"]
    assert {member.name for member in enum_type} == {
        "MANIFEST_PATH_INVALID",
        "MANIFEST_NOT_FOUND",
        "MANIFEST_READ_ERROR",
        "MALFORMED_JSON",
        "DUPLICATE_FIELD",
        "MANIFEST_SCHEMA_INVALID",
        "UNSUPPORTED_SCHEMA_VERSION",
        "STARTUP_TARGET_NOT_FOUND",
        "STARTUP_TARGET_INVALID",
    }
    expected_fields = {
        "RuntimeEntryResolutionDiagnostic": {
            "code": "RuntimeEntryResolutionFailureCode",
            "field_name": "str | None",
        },
        "RuntimeEntryResolutionFailure": {"diagnostic": "RuntimeEntryResolutionDiagnostic"},
        "ResolvedPythonModuleTarget": {
            "kind": "Literal['python_module']",
            "module_name": "Literal['argus.runtime']",
            "origin_path": "Path",
        },
        "RuntimeEntryResolutionResult": {
            "startup_target": "ResolvedPythonModuleTarget",
            "expected_binding": "ExpectedEnvironmentBinding",
            "data_root_locator": "DataRootLocator",
        },
    }
    for name, field_annotations in expected_fields.items():
        value = module.__dict__[name]
        assert value.__module__ == MODULE_NAME
        assert value.__dataclass_params__.frozen is True
        assert {
            field.name: field.type for field in value.__dataclass_fields__.values()
        } == field_annotations


# RER-S-002
def test_rer_s_002_public_resolver_signature_is_exact() -> None:
    signature = inspect.signature(resolver(surface()))
    assert tuple(signature.parameters) == (
        "identity",
        "config_snapshot",
        "artificial_manifest_path",
    )
    assert {name: parameter.annotation for name, parameter in signature.parameters.items()} == {
        "identity": "RuntimeIdentity",
        "config_snapshot": "RuntimeConfigSnapshot",
        "artificial_manifest_path": "Path",
    }
    assert (
        signature.return_annotation
        == "RuntimeEntryResolutionResult | RuntimeEntryResolutionFailure"
    )


# RER-S-003
def test_rer_s_003_production_source_has_no_forbidden_responsibility_imports() -> None:
    findings = semantic_boundary_findings(inspect.getsource(surface()))
    assert not [finding for finding in findings if finding.rule.startswith("S003_")]


# RER-S-004
def test_rer_s_004_source_has_no_discovery_or_inference_mechanism() -> None:
    findings = semantic_boundary_findings(inspect.getsource(surface()))
    assert not [finding for finding in findings if finding.rule.startswith("S004_")]


# RER-S-005
def test_rer_s_005_candidate_inventory_is_exactly_78_primary_ids() -> None:
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    ids = [
        "-".join(node.name.split("_")[1:4]).upper()
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_rer_")
    ]
    expected = [
        *(f"RER-U-{n:03d}" for n in range(1, 21)),
        *(f"RER-C-{n:03d}" for n in range(1, 26)),
        *(f"RER-I-{n:03d}" for n in range(1, 7)),
        *(f"RER-S-{n:03d}" for n in range(1, 7)),
        *(f"RER-U-{n:03d}" for n in range(21, 23)),
        *(f"RER-C-{n:03d}" for n in range(26, 35)),
        *(f"RER-I-{n:03d}" for n in range(7, 9)),
        *(f"RER-S-{n:03d}" for n in range(7, 9)),
        *(f"RER-C-{n:03d}" for n in range(35, 38)),
        *(f"RER-I-{n:03d}" for n in range(9, 11)),
        "RER-S-009",
    ]
    assert len(ids) == len(set(ids)) == 78
    assert ids == expected
    strategy_ids = set(
        __import__("re").findall(r"`(RER-[UCIS]-\d{3})`", TEST_STRATEGY.read_text(encoding="utf-8"))
    )
    assert strategy_ids == set(expected)


# RER-S-006
def test_rer_s_006_scope_and_lifecycle_artifacts_remain_open_and_unchanged() -> None:
    contract = CONTRACT.read_text(encoding="utf-8")
    registry = REGISTRY.read_text(encoding="utf-8")
    assert "RUNTIME_ENTRY_RESOLUTION_CONTRACT_READY_FOR_TEST_STRATEGY" in contract
    rer_rows = [
        line for line in registry.splitlines() if line.startswith("| `RUNTIME-ENTRY-RESOLUTION` |")
    ]
    assert rer_rows and all("`IN_PROGRESS`" in row for row in rer_rows)
    assert MODULE_NAME == "argus.runtime.runtime_entry_resolution"


# Corrective revision IDs. Historical RER-U/C/I/S-001.. ranges remain bound above.


# RER-U-021
def test_rer_u_021_huge_integer_in_unknown_root_field_is_inert(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data = (
        b'{"future":'
        + (b"9" * 5000)
        + b',"schema_version":"0.1","startup":{"kind":"python_module","entry":"argus.runtime"}}'
    )
    module, result, origin = _controlled_success(tmp_path, monkeypatch, data)
    _assert_exact_success(module, result, origin, tmp_path)


# RER-U-022
def test_rer_u_022_huge_unknown_integer_does_not_mask_schema_precedence(tmp_path: Path) -> None:
    data = b'{"future":' + (b"9" * 5000) + b',"startup":{}}'
    _failure(tmp_path, data, "MANIFEST_SCHEMA_INVALID", "schema_version")


# RER-C-026
def test_rer_c_026_lexical_failure_skips_filesystem_and_finder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(importlib.util, "find_spec", forbidden)
    module = surface()
    result, error, exists_calls = observe_path_exists(
        lambda: resolver(module)(identity(), snapshot(tmp_path), Path("manifest.json"))
    )
    assert error is None
    assert_failure(result, module, "MANIFEST_PATH_INVALID", None)
    assert exists_calls == ()


# RER-C-027
def test_rer_c_027_absence_skips_read_parse_and_finder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(Path, "read_bytes", forbidden)
    monkeypatch.setattr(importlib.util, "find_spec", forbidden)
    module = surface()
    result = resolver(module)(
        identity(), snapshot(tmp_path), (tmp_path / "manifest.json").absolute()
    )
    assert_failure(result, module, "MANIFEST_NOT_FOUND", None)


# RER-C-028
def test_rer_c_028_read_failure_skips_parse_and_finder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = manifest(tmp_path)
    module = surface()

    def fail_read(_path: Path) -> bytes:
        raise PermissionError("sentinel read failure")

    monkeypatch.setattr(Path, "read_bytes", fail_read)
    monkeypatch.setattr(importlib.util, "find_spec", forbidden)
    result = resolver(module)(identity(), snapshot(tmp_path), path)
    assert_failure(result, module, "MANIFEST_READ_ERROR", None)


# RER-C-029
def test_rer_c_029_parse_failure_skips_schema_and_finder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = surface()
    monkeypatch.setattr(importlib.util, "find_spec", forbidden)
    result = resolver(module)(identity(), snapshot(tmp_path), manifest(tmp_path, b"{"))
    assert_failure(result, module, "MALFORMED_JSON", None)


# RER-C-030
def test_rer_c_030_schema_failure_skips_target_resolution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(importlib.util, "find_spec", forbidden)
    _failure(tmp_path, b"{}", "MANIFEST_SCHEMA_INVALID", "schema_version")


# RER-C-031
def test_rer_c_031_missing_spec_skips_origin_and_result_construction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = manifest(tmp_path)
    monkeypatch.setattr(importlib.util, "find_spec", _finder(None))
    module = surface()
    result = resolver(module)(identity(), snapshot(tmp_path), path)
    assert_failure(result, module, "STARTUP_TARGET_NOT_FOUND", "startup.entry")


# RER-C-032
def test_rer_c_032_invalid_origin_skips_binding_and_locator_construction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = surface()
    monkeypatch.setattr(
        importlib.util,
        "find_spec",
        _finder(SimpleNamespace(origin="built-in", submodule_search_locations=None)),
    )
    result = resolver(module)(identity(), snapshot(tmp_path), manifest(tmp_path))
    assert_failure(result, module, "STARTUP_TARGET_INVALID", "startup.entry")


# RER-C-033
@pytest.mark.parametrize("data", [VALID_MANIFEST, b"{"], ids=["success", "failure"])
def test_rer_c_033_never_compiles_executes_launches_networks_or_reads_clock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, data: bytes
) -> None:
    module = surface()
    del monkeypatch
    operation = lambda: resolver(module)(identity(), snapshot(tmp_path), manifest(tmp_path, data))
    _, events = observe_calls(
        operation,
        forbidden_callables=(
            builtins.compile,
            builtins.exec,
            importlib.import_module,
            *process_launch_callables(),
            socket.socket,
            time.time,
        ),
    )
    assert events == ()


# RER-C-034
def test_rer_c_034_never_mutates_manifest_or_target_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = manifest(tmp_path)
    before = path.read_bytes()
    monkeypatch.setattr(Path, "write_bytes", forbidden)
    monkeypatch.setattr(Path, "write_text", forbidden)
    resolver(surface())(identity(), snapshot(tmp_path), path)
    assert path.read_bytes() == before


# RER-I-007
@pytest.mark.parametrize("data", [VALID_MANIFEST, b"{"], ids=["success", "failure"])
def test_rer_i_007_never_calls_environment_binding_or_marker_boundaries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, data: bytes
) -> None:
    import argus.runtime.data_root_marker_store as marker_store
    import argus.runtime.environment_binding as binding

    del monkeypatch
    module = surface()
    _, events = observe_calls(
        lambda: resolver(module)(identity(), snapshot(tmp_path), manifest(tmp_path, data)),
        forbidden_callables=(
            binding.verify_environment_binding,
            marker_store.load_data_root_marker,
            marker_store.initialize_data_root_marker,
        ),
    )
    assert events == ()


# RER-I-008
def test_rer_i_008_environment_comes_only_from_identity_not_environment_or_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    live_path = (tmp_path / "LIVE" / "manifest.json").absolute()
    live_path.parent.mkdir()
    live_path.write_bytes(VALID_MANIFEST)
    module, result, origin = _controlled_success(tmp_path, monkeypatch)
    result, events = observe_calls(
        lambda: resolver(module)(identity(Environment.TEST), snapshot(tmp_path), live_path),
        forbidden_callables=(os.getenv, os.getcwd),
    )
    assert events == ()
    _assert_exact_success(module, result, origin, tmp_path)


# RER-S-007
def test_rer_s_007_public_types_use_ordinary_static_declarations() -> None:
    assert public_type_contract_violations(surface()) == ()


# RER-S-008
def test_rer_s_008_corrective_inventory_and_strategy_traceability_are_exact() -> None:
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    ids = [
        "-".join(node.name.split("_")[1:4]).upper()
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_rer_")
    ]
    assert len(ids) == len(set(ids)) == 78
    strategy_ids = set(
        __import__("re").findall(r"`(RER-[UCIS]-\d{3})`", TEST_STRATEGY.read_text(encoding="utf-8"))
    )
    assert set(ids) == strategy_ids


# v0.3 successor IDs.  The v0.2 IDs above remain historical and are not repurposed.


# RER-C-035 (successor to aggregated RER-C-021/RER-C-034 write assurance)
@pytest.mark.parametrize("data", [VALID_MANIFEST, b"{"], ids=["success", "terminal-failure"])
def test_rer_c_035_manifest_target_and_marker_bytes_are_unchanged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, data: bytes
) -> None:
    manifest_path = manifest(tmp_path, data)
    target = tmp_path / "pkg" / "__init__.py"
    target.parent.mkdir()
    target.write_bytes(b"target-sentinel")
    data_root = (tmp_path / "actual-data-root").absolute()
    data_root.mkdir()
    (data_root / "existing-marker-state.json").write_bytes(b"marker-sentinel")
    alternate = data_root / "nested" / "alternate-state.bin"
    alternate.parent.mkdir()
    alternate.write_bytes(b"alternate-sentinel")
    monkeypatch.setattr(
        importlib.util,
        "find_spec",
        _finder(
            SimpleNamespace(origin=str(target), submodule_search_locations=[str(target.parent)])
        ),
    )
    before_files = byte_snapshot((manifest_path, target))
    before_data_root = directory_snapshot(data_root)
    resolver(surface())(identity(), snapshot(tmp_path, data_root), manifest_path)
    assert byte_snapshot((manifest_path, target)) == before_files
    assert directory_snapshot(data_root) == before_data_root


# RER-C-036 (successor to permissive RER-C-022)
def test_rer_c_036_determinism_requires_exact_success_outcome(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module, first, origin = _controlled_success(tmp_path, monkeypatch)
    other = tmp_path / "other-cwd"
    other.mkdir()
    monkeypatch.chdir(other)
    monkeypatch.setenv("ARGUS_ENV", "LIVE")
    second = resolver(module)(identity(), snapshot(tmp_path), manifest(tmp_path))
    _assert_exact_success(module, first, origin, tmp_path)
    _assert_exact_success(module, second, origin, tmp_path)
    assert second == first


# RER-C-037 (Contract §2 typed-domain clarification; no invented widening)
def test_rer_c_037_public_path_parameter_remains_typed_path() -> None:
    parameter = inspect.signature(resolver(surface())).parameters["artificial_manifest_path"]
    assert parameter.annotation == "Path"


# RER-I-009 (successor to RER-I-005/RER-I-007 and S-003 runtime assurance)
@pytest.mark.parametrize("data", [VALID_MANIFEST, b"{"], ids=["success", "terminal-failure"])
def test_rer_i_009_no_upstream_or_later_boundary_is_invoked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, data: bytes
) -> None:
    path = manifest(tmp_path, data)
    if data == VALID_MANIFEST:
        target = tmp_path / "pkg-i009" / "__init__.py"
        target.parent.mkdir()
        target.write_bytes(b"target")
        monkeypatch.setattr(
            importlib.util,
            "find_spec",
            _finder(
                SimpleNamespace(origin=str(target), submodule_search_locations=[str(target.parent)])
            ),
        )
    module = surface()
    _, events = observe_calls(lambda: resolver(module)(identity(), snapshot(tmp_path), path))
    assert events == ()


# RER-I-010 (successor to permissive RER-I-008)
def test_rer_i_010_environment_mapping_requires_exact_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module, result, origin = _controlled_success(tmp_path, monkeypatch)
    _assert_exact_success(module, result, origin, tmp_path)
    assert vars(vars(result)["expected_binding"])["environment"] is Environment.TEST


# RER-S-009 (semantic successor to source-shape-coupled RER-S-007)
def test_rer_s_009_public_type_contract_is_semantic_not_source_shape() -> None:
    assert public_type_contract_violations(surface()) == ()
