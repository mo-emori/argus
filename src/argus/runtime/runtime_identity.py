import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any, cast
from uuid import RFC_4122, UUID

from argus.runtime.environment import Environment

_FIELD_NAMES = (
    "schema_version",
    "state_id",
    "data_root_id",
    "environment",
    "created_at",
)
_FIELD_NAME_SET = frozenset(_FIELD_NAMES)
_UUID_V4_PATTERN = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}"
)
_RFC3339_PATTERN = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T"
    r"[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]{1,6})?"
    r"(?:Z|[+-][0-9]{2}:[0-9]{2})"
)


class RuntimeIdentityValidationErrorCode(str, Enum):
    MALFORMED_JSON = "MALFORMED_JSON"
    JSON_ROOT_NOT_OBJECT = "JSON_ROOT_NOT_OBJECT"
    MISSING_FIELD = "MISSING_FIELD"
    UNKNOWN_FIELD = "UNKNOWN_FIELD"
    DUPLICATE_FIELD = "DUPLICATE_FIELD"
    INVALID_FIELD_TYPE = "INVALID_FIELD_TYPE"
    UNSUPPORTED_SCHEMA_VERSION = "UNSUPPORTED_SCHEMA_VERSION"
    INVALID_STATE_ID = "INVALID_STATE_ID"
    INVALID_DATA_ROOT_ID = "INVALID_DATA_ROOT_ID"
    INVALID_ENVIRONMENT = "INVALID_ENVIRONMENT"
    INVALID_CREATED_AT = "INVALID_CREATED_AT"


@dataclass(frozen=True)
class RuntimeIdentityValidationError:
    code: RuntimeIdentityValidationErrorCode
    field_name: str | None = None


@dataclass(frozen=True)
class RuntimeIdentityValidationFailure:
    errors: tuple[RuntimeIdentityValidationError, ...]

    def __post_init__(self) -> None:
        if not self.errors:
            raise ValueError("errors must be non-empty")


def _is_uuid_v4(value: object) -> bool:
    return (
        isinstance(value, UUID)
        and value.version == 4
        and value.variant == RFC_4122
    )


def _is_aware_datetime(value: object) -> bool:
    if not isinstance(value, datetime):
        return False
    try:
        return value.utcoffset() is not None
    except (OverflowError, ValueError):
        return False


def _is_environment(value: object) -> bool:
    return isinstance(value, Environment)


@dataclass(frozen=True)
class RuntimeIdentity:
    schema_version: int
    state_id: UUID
    data_root_id: UUID
    environment: Environment
    created_at: datetime

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise ValueError("schema_version must be integer 1")
        if not _is_uuid_v4(self.state_id):
            raise ValueError("state_id must be a UUID v4")
        if not _is_uuid_v4(self.data_root_id):
            raise ValueError("data_root_id must be a UUID v4")
        if not _is_environment(self.environment):
            raise ValueError("environment must be an Environment")
        if not _is_aware_datetime(self.created_at):
            raise ValueError("created_at must be timezone-aware")


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


def _failure(
    code: RuntimeIdentityValidationErrorCode,
    field_name: str | None = None,
) -> RuntimeIdentityValidationFailure:
    return RuntimeIdentityValidationFailure(
        errors=(RuntimeIdentityValidationError(code, field_name),)
    )


def _parse_uuid_v4(value: str) -> UUID | None:
    if _UUID_V4_PATTERN.fullmatch(value) is None:
        return None
    try:
        parsed = UUID(value)
    except ValueError:
        return None
    if str(parsed) != value or not _is_uuid_v4(parsed):
        return None
    return parsed


def _parse_rfc3339(value: str) -> datetime | None:
    if _RFC3339_PATTERN.fullmatch(value) is None:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.utcoffset() is None:
        return None
    return parsed


def parse_runtime_identity(
    data: bytes,
) -> RuntimeIdentity | RuntimeIdentityValidationFailure:
    try:
        text = data.decode("utf-8")
        parsed_document = json.loads(
            text,
            object_pairs_hook=_object_from_pairs,
            parse_constant=_reject_non_standard_constant,
        )
    except _DuplicateFieldError as exc:
        return _failure(
            RuntimeIdentityValidationErrorCode.DUPLICATE_FIELD,
            exc.field_name,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return _failure(RuntimeIdentityValidationErrorCode.MALFORMED_JSON)

    if not isinstance(parsed_document, dict):
        return _failure(RuntimeIdentityValidationErrorCode.JSON_ROOT_NOT_OBJECT)
    document = cast(dict[str, object], parsed_document)

    schema_errors = [
        RuntimeIdentityValidationError(
            RuntimeIdentityValidationErrorCode.MISSING_FIELD,
            field_name,
        )
        for field_name in _FIELD_NAMES
        if field_name not in document
    ]
    schema_errors.extend(
        RuntimeIdentityValidationError(
            RuntimeIdentityValidationErrorCode.UNKNOWN_FIELD,
            field_name,
        )
        for field_name in document
        if field_name not in _FIELD_NAME_SET
    )
    if schema_errors:
        return RuntimeIdentityValidationFailure(tuple(schema_errors))

    expected_types: dict[str, type[object]] = {
        "schema_version": int,
        "state_id": str,
        "data_root_id": str,
        "environment": str,
        "created_at": str,
    }
    type_errors = tuple(
        RuntimeIdentityValidationError(
            RuntimeIdentityValidationErrorCode.INVALID_FIELD_TYPE,
            field_name,
        )
        for field_name in _FIELD_NAMES
        if type(document[field_name]) is not expected_types[field_name]
    )
    if type_errors:
        return RuntimeIdentityValidationFailure(type_errors)

    schema_version = cast(int, document["schema_version"])
    state_id_text = cast(str, document["state_id"])
    data_root_id_text = cast(str, document["data_root_id"])
    environment_text = cast(str, document["environment"])
    created_at_text = cast(str, document["created_at"])

    state_id = _parse_uuid_v4(state_id_text)
    data_root_id = _parse_uuid_v4(data_root_id_text)
    try:
        environment = Environment(environment_text)
    except ValueError:
        environment = None
    created_at = _parse_rfc3339(created_at_text)

    domain_errors: list[RuntimeIdentityValidationError] = []
    if schema_version != 1:
        domain_errors.append(
            RuntimeIdentityValidationError(
                RuntimeIdentityValidationErrorCode.UNSUPPORTED_SCHEMA_VERSION,
                "schema_version",
            )
        )
    if state_id is None:
        domain_errors.append(
            RuntimeIdentityValidationError(
                RuntimeIdentityValidationErrorCode.INVALID_STATE_ID,
                "state_id",
            )
        )
    if data_root_id is None:
        domain_errors.append(
            RuntimeIdentityValidationError(
                RuntimeIdentityValidationErrorCode.INVALID_DATA_ROOT_ID,
                "data_root_id",
            )
        )
    if environment is None:
        domain_errors.append(
            RuntimeIdentityValidationError(
                RuntimeIdentityValidationErrorCode.INVALID_ENVIRONMENT,
                "environment",
            )
        )
    if created_at is None:
        domain_errors.append(
            RuntimeIdentityValidationError(
                RuntimeIdentityValidationErrorCode.INVALID_CREATED_AT,
                "created_at",
            )
        )
    if domain_errors:
        return RuntimeIdentityValidationFailure(tuple(domain_errors))

    if (
        state_id is None
        or data_root_id is None
        or environment is None
        or created_at is None
    ):
        raise RuntimeError("validated Runtime Identity values are unavailable")
    return RuntimeIdentity(
        schema_version=schema_version,
        state_id=state_id,
        data_root_id=data_root_id,
        environment=environment,
        created_at=created_at,
    )


def _require_runtime_identity(value: object) -> RuntimeIdentity:
    if not isinstance(value, RuntimeIdentity):
        raise TypeError("identity must be a RuntimeIdentity")
    return value


def serialize_runtime_identity(identity: RuntimeIdentity) -> bytes:
    identity = _require_runtime_identity(identity)
    try:
        RuntimeIdentity(
            schema_version=identity.schema_version,
            state_id=identity.state_id,
            data_root_id=identity.data_root_id,
            environment=identity.environment,
            created_at=identity.created_at,
        )
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError("identity violates RuntimeIdentity invariants") from exc

    utc_created_at = identity.created_at.astimezone(UTC)
    created_at = utc_created_at.strftime("%Y-%m-%dT%H:%M:%S")
    if utc_created_at.microsecond:
        created_at += f".{utc_created_at.microsecond:06d}"
    created_at += "Z"

    document = {
        "schema_version": identity.schema_version,
        "state_id": str(identity.state_id),
        "data_root_id": str(identity.data_root_id),
        "environment": identity.environment.value,
        "created_at": created_at,
    }
    return (
        json.dumps(document, ensure_ascii=False, allow_nan=False, indent=2)
        + "\n"
    ).encode("utf-8")
