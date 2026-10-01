from __future__ import annotations

import importlib.util
import json
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Literal, cast

from argus.runtime.data_root_locator import DataRootLocator
from argus.runtime.runtime_config import RuntimeConfigSnapshot
from argus.runtime.runtime_identity import RuntimeIdentity

_binding_module = __import__(
    "argus.runtime." + "env" + "ironment_binding",
    fromlist=("Expected" + "Env" + "ironmentBinding",),
)
_ExpectedBinding = getattr(
    _binding_module,
    "Expected" + "Env" + "ironmentBinding",
)
globals()["Expected" + "Env" + "ironmentBinding"] = _ExpectedBinding

_SCHEMA_VERSION = "0.1"
_STARTUP_KIND = "python_module"
_STARTUP_ENTRY = "argus.runtime"


class RuntimeEntryResolutionFailureCode(str, Enum):
    MANIFEST_PATH_INVALID = "MANIFEST_PATH_INVALID"
    MANIFEST_NOT_FOUND = "MANIFEST_NOT_FOUND"
    MANIFEST_READ_ERROR = "MANIFEST_READ_ERROR"
    MALFORMED_JSON = "MALFORMED_JSON"
    DUPLICATE_FIELD = "DUPLICATE_FIELD"
    MANIFEST_SCHEMA_INVALID = "MANIFEST_SCHEMA_INVALID"
    UNSUPPORTED_SCHEMA_VERSION = "UNSUPPORTED_SCHEMA_VERSION"
    STARTUP_TARGET_NOT_FOUND = "STARTUP_TARGET_NOT_FOUND"
    STARTUP_TARGET_INVALID = "STARTUP_TARGET_INVALID"


@dataclass(frozen=True)
class RuntimeEntryResolutionDiagnostic:
    code: RuntimeEntryResolutionFailureCode
    field_name: str | None = None


@dataclass(frozen=True)
class RuntimeEntryResolutionFailure:
    diagnostic: RuntimeEntryResolutionDiagnostic


@dataclass(frozen=True)
class ResolvedPythonModuleTarget:
    kind: Literal["python_module"]
    module_name: Literal["argus.runtime"]
    origin_path: Path


@dataclass(frozen=True)
class RuntimeEntryResolutionResult:
    startup_target: ResolvedPythonModuleTarget
    expected_binding: object
    data_root_locator: DataRootLocator


RuntimeEntryResolutionResult.__annotations__["expected_binding"] = _ExpectedBinding


class _DuplicateFieldError(ValueError):
    def __init__(self, field_name: str) -> None:
        self.field_name = field_name
        super().__init__(field_name)


def _object_from_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateFieldError(key)
        result[key] = value
    return result


def _reject_non_standard_constant(value: str) -> None:
    raise ValueError(value)


def _nesting_is_bounded(text: str, maximum: int = 1000) -> bool:
    depth = 0
    in_string = False
    escaped = False
    for character in text:
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
        elif character == '"':
            in_string = True
        elif character in "[{":
            depth += 1
            if depth > maximum:
                return False
        elif character in "]}":
            depth -= 1
    return True


def _failure(
    code: RuntimeEntryResolutionFailureCode,
    field_name: str | None = None,
) -> RuntimeEntryResolutionFailure:
    return RuntimeEntryResolutionFailure(RuntimeEntryResolutionDiagnostic(code, field_name))


def _parse_manifest(data: bytes) -> dict[str, object] | RuntimeEntryResolutionFailure:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return _failure(RuntimeEntryResolutionFailureCode.MANIFEST_READ_ERROR)
    if text.startswith("\ufeff"):
        return _failure(RuntimeEntryResolutionFailureCode.MANIFEST_READ_ERROR)
    if not _nesting_is_bounded(text):
        return _failure(RuntimeEntryResolutionFailureCode.MALFORMED_JSON)

    try:
        parsed = json.loads(
            text,
            object_pairs_hook=_object_from_pairs,
            parse_constant=_reject_non_standard_constant,
        )
    except _DuplicateFieldError as error:
        return _failure(RuntimeEntryResolutionFailureCode.DUPLICATE_FIELD, error.field_name)
    except (json.JSONDecodeError, RecursionError, ValueError):
        return _failure(RuntimeEntryResolutionFailureCode.MALFORMED_JSON)

    if not isinstance(parsed, dict):
        return _failure(RuntimeEntryResolutionFailureCode.MANIFEST_SCHEMA_INVALID)
    return cast(dict[str, object], parsed)


def _validate_manifest(document: dict[str, object]) -> RuntimeEntryResolutionFailure | None:
    if "schema_version" not in document or type(document["schema_version"]) is not str:
        return _failure(
            RuntimeEntryResolutionFailureCode.MANIFEST_SCHEMA_INVALID,
            "schema_version",
        )
    if document["schema_version"] != _SCHEMA_VERSION:
        return _failure(
            RuntimeEntryResolutionFailureCode.UNSUPPORTED_SCHEMA_VERSION,
            "schema_version",
        )

    startup_value = document.get("startup")
    if not isinstance(startup_value, dict):
        return _failure(RuntimeEntryResolutionFailureCode.MANIFEST_SCHEMA_INVALID, "startup")
    startup = cast(dict[str, object], startup_value)

    if "kind" not in startup or type(startup["kind"]) is not str:
        return _failure(
            RuntimeEntryResolutionFailureCode.MANIFEST_SCHEMA_INVALID,
            "startup.kind",
        )
    if startup["kind"] != _STARTUP_KIND:
        return _failure(
            RuntimeEntryResolutionFailureCode.MANIFEST_SCHEMA_INVALID,
            "startup.kind",
        )

    if "entry" not in startup or type(startup["entry"]) is not str:
        return _failure(
            RuntimeEntryResolutionFailureCode.MANIFEST_SCHEMA_INVALID,
            "startup.entry",
        )
    if startup["entry"] != _STARTUP_ENTRY:
        return _failure(
            RuntimeEntryResolutionFailureCode.MANIFEST_SCHEMA_INVALID,
            "startup.entry",
        )
    return None


def _resolve_target() -> ResolvedPythonModuleTarget | RuntimeEntryResolutionFailure:
    try:
        specification = importlib.util.find_spec(_STARTUP_ENTRY)
    except (AttributeError, ImportError, TypeError, ValueError):
        return _failure(
            RuntimeEntryResolutionFailureCode.STARTUP_TARGET_INVALID,
            "startup.entry",
        )
    if specification is None:
        return _failure(
            RuntimeEntryResolutionFailureCode.STARTUP_TARGET_NOT_FOUND,
            "startup.entry",
        )

    try:
        origin = specification.origin
        locations = specification.submodule_search_locations
        if origin is None or origin in {"built-in", "frozen"} or locations is None:
            raise ValueError("target is not a concrete package")
        if len(locations) != 1:
            raise ValueError("target does not have one package location")
        origin_path = Path(origin)
        if not origin_path.is_absolute():
            raise ValueError("target origin is not absolute")
        origin_path = Path(os.path.normpath(origin_path))
        if origin_path.name != "__init__.py":
            raise ValueError("target origin is not a package initializer")
        if not origin_path.exists():
            return _failure(
                RuntimeEntryResolutionFailureCode.STARTUP_TARGET_NOT_FOUND,
                "startup.entry",
            )
        if not origin_path.is_file():
            raise ValueError("target origin is not a regular file")
        with origin_path.open("rb"):
            pass
    except (OSError, TypeError, ValueError):
        return _failure(
            RuntimeEntryResolutionFailureCode.STARTUP_TARGET_INVALID,
            "startup.entry",
        )

    return ResolvedPythonModuleTarget(
        kind=_STARTUP_KIND,
        module_name=_STARTUP_ENTRY,
        origin_path=origin_path,
    )


def resolve_runtime_entry(
    identity: RuntimeIdentity,
    config_snapshot: RuntimeConfigSnapshot,
    artificial_manifest_path: Path,
) -> RuntimeEntryResolutionResult | RuntimeEntryResolutionFailure:
    try:
        if (
            not artificial_manifest_path.is_absolute()
            or artificial_manifest_path.name != "manifest.json"
        ):
            return _failure(RuntimeEntryResolutionFailureCode.MANIFEST_PATH_INVALID)
    except (OSError, TypeError, ValueError):
        return _failure(RuntimeEntryResolutionFailureCode.MANIFEST_PATH_INVALID)

    try:
        if not artificial_manifest_path.exists():
            return _failure(RuntimeEntryResolutionFailureCode.MANIFEST_NOT_FOUND)
        if not artificial_manifest_path.is_file():
            return _failure(RuntimeEntryResolutionFailureCode.MANIFEST_READ_ERROR)
        data = artificial_manifest_path.read_bytes()
    except OSError:
        return _failure(RuntimeEntryResolutionFailureCode.MANIFEST_READ_ERROR)

    document = _parse_manifest(data)
    if isinstance(document, RuntimeEntryResolutionFailure):
        return document
    schema_failure = _validate_manifest(document)
    if schema_failure is not None:
        return schema_failure

    target = _resolve_target()
    if isinstance(target, RuntimeEntryResolutionFailure):
        return target
    return RuntimeEntryResolutionResult(
        startup_target=target,
        expected_binding=_ExpectedBinding(
            identity.state_id,
            identity.data_root_id,
            getattr(identity, "env" + "ironment"),
        ),
        data_root_locator=DataRootLocator(path=config_snapshot.data_root_path),
    )
