import json
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, cast

_FIELD_NAMES = ("config_version", "data_root")
_FIELD_NAME_SET = frozenset(_FIELD_NAMES)


class RuntimeConfigState(str, Enum):
    CONFIGURED = "CONFIGURED"
    UNCONFIGURED = "UNCONFIGURED"
    INVALID = "INVALID"
    ERROR = "ERROR"


class RuntimeConfigDiagnosticCode(str, Enum):
    CONFIG_NOT_FOUND = "CONFIG_NOT_FOUND"
    CONFIG_READ_ERROR = "CONFIG_READ_ERROR"
    DATA_ROOT_RESOLUTION_ERROR = "DATA_ROOT_RESOLUTION_ERROR"
    MALFORMED_JSON = "MALFORMED_JSON"
    JSON_ROOT_NOT_OBJECT = "JSON_ROOT_NOT_OBJECT"
    DUPLICATE_KEY = "DUPLICATE_KEY"
    MISSING_FIELD = "MISSING_FIELD"
    UNKNOWN_KEY = "UNKNOWN_KEY"
    INVALID_FIELD_TYPE = "INVALID_FIELD_TYPE"
    UNSUPPORTED_CONFIG_VERSION = "UNSUPPORTED_CONFIG_VERSION"
    INVALID_DATA_ROOT = "INVALID_DATA_ROOT"


@dataclass(frozen=True)
class RuntimeConfigDiagnostic:
    code: RuntimeConfigDiagnosticCode
    field_name: str | None = None


@dataclass(frozen=True)
class ValidatedRuntimeConfig:
    config_version: int
    data_root: str


@dataclass(frozen=True)
class RuntimeConfigSnapshot:
    config_version: int
    data_root: str
    config_path: Path
    data_root_path: Path


@dataclass(frozen=True)
class RuntimeConfigResult:
    state: RuntimeConfigState
    snapshot: ValidatedRuntimeConfig | RuntimeConfigSnapshot | None
    diagnostics: tuple[RuntimeConfigDiagnostic, ...]


class _DuplicateKeyError(ValueError):
    def __init__(self, key: str) -> None:
        self.key = key
        super().__init__(key)


def _object_from_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError(key)
        result[key] = value
    return result


def _reject_non_standard_constant(value: str) -> None:
    raise ValueError(value)


def _failure(
    state: RuntimeConfigState,
    code: RuntimeConfigDiagnosticCode,
    field_name: str | None = None,
) -> RuntimeConfigResult:
    return RuntimeConfigResult(
        state=state,
        snapshot=None,
        diagnostics=(RuntimeConfigDiagnostic(code, field_name),),
    )


def _invalid(diagnostics: list[RuntimeConfigDiagnostic]) -> RuntimeConfigResult:
    return RuntimeConfigResult(
        state=RuntimeConfigState.INVALID,
        snapshot=None,
        diagnostics=tuple(diagnostics),
    )


def _is_valid_data_root(value: str) -> bool:
    if not value or "\x00" in value or value[0] in "/\\":
        return False
    return not (
        len(value) >= 2
        and ("A" <= value[0] <= "Z" or "a" <= value[0] <= "z")
        and value[1] == ":"
    )


def parse_runtime_config(data: bytes) -> RuntimeConfigResult:
    try:
        text = data.decode("utf-8")
        if text.startswith("\ufeff"):
            raise ValueError("UTF-8 BOM is not accepted")
        parsed = json.loads(
            text,
            object_pairs_hook=_object_from_pairs,
            parse_constant=_reject_non_standard_constant,
        )
    except _DuplicateKeyError as error:
        return _failure(
            RuntimeConfigState.INVALID,
            RuntimeConfigDiagnosticCode.DUPLICATE_KEY,
            error.key,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return _failure(
            RuntimeConfigState.INVALID,
            RuntimeConfigDiagnosticCode.MALFORMED_JSON,
        )

    if not isinstance(parsed, dict):
        return _failure(
            RuntimeConfigState.INVALID,
            RuntimeConfigDiagnosticCode.JSON_ROOT_NOT_OBJECT,
        )
    document = cast(dict[str, object], parsed)

    structural_diagnostics = [
        RuntimeConfigDiagnostic(RuntimeConfigDiagnosticCode.MISSING_FIELD, field_name)
        for field_name in _FIELD_NAMES
        if field_name not in document
    ]
    structural_diagnostics.extend(
        RuntimeConfigDiagnostic(RuntimeConfigDiagnosticCode.UNKNOWN_KEY, field_name)
        for field_name in document
        if field_name not in _FIELD_NAME_SET
    )
    if structural_diagnostics:
        return _invalid(structural_diagnostics)

    expected_types: dict[str, type[object]] = {
        "config_version": int,
        "data_root": str,
    }
    type_diagnostics = [
        RuntimeConfigDiagnostic(RuntimeConfigDiagnosticCode.INVALID_FIELD_TYPE, field_name)
        for field_name in _FIELD_NAMES
        if type(document[field_name]) is not expected_types[field_name]
    ]
    if type_diagnostics:
        return _invalid(type_diagnostics)

    config_version = cast(int, document["config_version"])
    data_root = cast(str, document["data_root"])
    value_diagnostics: list[RuntimeConfigDiagnostic] = []
    if config_version != 1:
        value_diagnostics.append(
            RuntimeConfigDiagnostic(
                RuntimeConfigDiagnosticCode.UNSUPPORTED_CONFIG_VERSION,
                "config_version",
            )
        )
    if not _is_valid_data_root(data_root):
        value_diagnostics.append(
            RuntimeConfigDiagnostic(RuntimeConfigDiagnosticCode.INVALID_DATA_ROOT, "data_root")
        )
    if value_diagnostics:
        return _invalid(value_diagnostics)

    return RuntimeConfigResult(
        state=RuntimeConfigState.CONFIGURED,
        snapshot=ValidatedRuntimeConfig(config_version=config_version, data_root=data_root),
        diagnostics=(),
    )


def load_runtime_config(config_path: Path) -> RuntimeConfigResult:
    if not config_path.is_absolute() or config_path.name != "config.json":
        raise ValueError("config_path must be an absolute path ending in config.json")

    normalized_config_path = Path(os.path.normpath(os.path.abspath(config_path)))
    try:
        data = config_path.read_bytes()
    except FileNotFoundError:
        if config_path.is_symlink():
            return _failure(
                RuntimeConfigState.ERROR,
                RuntimeConfigDiagnosticCode.CONFIG_READ_ERROR,
            )
        return _failure(
            RuntimeConfigState.UNCONFIGURED,
            RuntimeConfigDiagnosticCode.CONFIG_NOT_FOUND,
        )
    except OSError:
        return _failure(
            RuntimeConfigState.ERROR,
            RuntimeConfigDiagnosticCode.CONFIG_READ_ERROR,
        )

    parsed = parse_runtime_config(data)
    if parsed.state is not RuntimeConfigState.CONFIGURED:
        return parsed
    validated = cast(ValidatedRuntimeConfig, parsed.snapshot)

    try:
        data_root_path = Path(
            os.path.normpath(normalized_config_path.parent / validated.data_root)
        )
        if not data_root_path.is_absolute():
            raise ValueError("Data Root resolution did not produce an absolute path")
    except (OSError, TypeError, ValueError):
        return _failure(
            RuntimeConfigState.ERROR,
            RuntimeConfigDiagnosticCode.DATA_ROOT_RESOLUTION_ERROR,
            "data_root",
        )

    return RuntimeConfigResult(
        state=RuntimeConfigState.CONFIGURED,
        snapshot=RuntimeConfigSnapshot(
            config_version=validated.config_version,
            data_root=validated.data_root,
            config_path=normalized_config_path,
            data_root_path=data_root_path,
        ),
        diagnostics=(),
    )
