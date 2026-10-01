from __future__ import annotations

import importlib
import json
from collections.abc import Callable
from dataclasses import fields, is_dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from types import ModuleType
from typing import Protocol, cast
from uuid import UUID

import pytest

from argus.runtime.environment import Environment
from argus.runtime.runtime_config import RuntimeConfigSnapshot
from argus.runtime.runtime_identity import RuntimeIdentity

MODULE_NAME = "argus.runtime.runtime_entry_resolution"
PUBLIC_SYMBOLS = frozenset(
    {
        "DataRootLocator",
        "ExpectedEnvironmentBinding",
        "ResolvedPythonModuleTarget",
        "RuntimeEntryResolutionDiagnostic",
        "RuntimeEntryResolutionFailure",
        "RuntimeEntryResolutionFailureCode",
        "RuntimeEntryResolutionResult",
        "resolve_runtime_entry",
    }
)
VALID_MANIFEST = (
    b'{"schema_version":"0.1","startup":{"kind":"python_module","entry":"argus.runtime"}}'
)


class Resolver(Protocol):
    def __call__(
        self,
        identity: RuntimeIdentity,
        config_snapshot: RuntimeConfigSnapshot,
        artificial_manifest_path: Path,
    ) -> object: ...


def surface() -> ModuleType:
    try:
        module = importlib.import_module(MODULE_NAME)
    except ModuleNotFoundError as exc:
        if exc.name != MODULE_NAME:
            raise
        pytest.fail(
            "EXPECTED_ABSENT_PRODUCTION_SURFACE: "
            "argus.runtime.runtime_entry_resolution is not implemented"
        )
    missing = sorted(PUBLIC_SYMBOLS.difference(module.__dict__))
    if missing:
        pytest.fail(f"EXPECTED_INCOMPLETE_PRODUCTION_SURFACE: missing {missing}")
    return module


def resolver(module: ModuleType) -> Resolver:
    return cast(Resolver, module.__dict__["resolve_runtime_entry"])


def identity(environment: Environment = Environment.TEST) -> RuntimeIdentity:
    return RuntimeIdentity(
        schema_version=1,
        state_id=UUID("12345678-1234-4234-9234-123456789abc"),
        data_root_id=UUID("87654321-4321-4321-8321-cba987654321"),
        environment=environment,
        created_at=datetime(2026, 10, 1, tzinfo=UTC),
    )


def snapshot(tmp_path: Path, data_root_path: Path | None = None) -> RuntimeConfigSnapshot:
    return RuntimeConfigSnapshot(
        config_version=1,
        data_root="sentinel-data-root",
        config_path=(tmp_path / "config.json").absolute(),
        data_root_path=data_root_path or (tmp_path / "sentinel-data-root").absolute(),
    )


def manifest(tmp_path: Path, data: bytes = VALID_MANIFEST) -> Path:
    path = (tmp_path / "manifest.json").absolute()
    path.write_bytes(data)
    return path


def invoke(tmp_path: Path, data: bytes = VALID_MANIFEST) -> tuple[ModuleType, object]:
    module = surface()
    result = resolver(module)(identity(), snapshot(tmp_path), manifest(tmp_path, data))
    return module, result


def enum_value(module: ModuleType, name: str) -> object:
    enum_type = cast(type[Enum], module.__dict__["RuntimeEntryResolutionFailureCode"])
    return enum_type[name]


def assert_failure(result: object, module: ModuleType, code: str, field: str | None) -> None:
    failure_type = cast(type[object], module.__dict__["RuntimeEntryResolutionFailure"])
    diagnostic_type = cast(
        Callable[..., object], module.__dict__["RuntimeEntryResolutionDiagnostic"]
    )
    assert type(result) is failure_type
    assert vars(result) == {
        "diagnostic": diagnostic_type(code=enum_value(module, code), field_name=field)
    }


def assert_closed_dataclass(value: object, expected: tuple[str, ...]) -> None:
    assert is_dataclass(value) and not isinstance(value, type)
    assert tuple(field.name for field in fields(value)) == expected


def json_bytes(document: object) -> bytes:
    return json.dumps(document, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def forbidden(*_args: object, **_kwargs: object) -> object:
    raise AssertionError("prohibited downstream boundary was called")


def callable_symbol(module: ModuleType, name: str) -> Callable[..., object]:
    return cast(Callable[..., object], module.__dict__[name])
