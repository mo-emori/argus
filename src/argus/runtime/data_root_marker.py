import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import cast
from uuid import UUID

from argus.runtime.environment import Environment

_FIELD_NAMES = (
    "schema_version",
    "state_id",
    "data_root_id",
    "environment",
    "created_at",
)
_FIELD_NAME_SET = frozenset(_FIELD_NAMES)
_CANONICAL_UUID_PATTERN = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
)
_RFC3339_PATTERN = re.compile(
    r"(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})T"
    r"(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})"
    r"(?P<fraction>\.[0-9]{1,6})?"
    r"(?P<offset>Z|[+-][0-9]{2}:[0-9]{2})"
)


class MarkerValidationErrorCode(str, Enum):
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
class MarkerValidationError:
    code: MarkerValidationErrorCode
    field_name: str | None = None


@dataclass(frozen=True)
class MarkerValidationFailure:
    errors: tuple[MarkerValidationError, ...]

    def __post_init__(self) -> None:
        if not self.errors:
            raise ValueError("errors must not be empty")


@dataclass(frozen=True)
class DataRootMarker:
    schema_version: int
    state_id: UUID
    data_root_id: UUID
    environment: Environment
    created_at: datetime

    def __post_init__(self) -> None:
        _validate_marker_invariants(
            self.schema_version,
            self.state_id,
            self.data_root_id,
            self.environment,
            self.created_at,
        )


def _validate_marker_invariants(
    schema_version: object,
    state_id: object,
    data_root_id: object,
    environment: object,
    created_at: object,
) -> None:
    if type(schema_version) is not int or schema_version != 1:
        raise ValueError("schema_version must be integer 1")
    if not isinstance(state_id, UUID) or state_id.version != 4:
        raise ValueError("state_id must be a UUID v4")
    if not isinstance(data_root_id, UUID) or data_root_id.version != 4:
        raise ValueError("data_root_id must be a UUID v4")
    if not isinstance(environment, Environment):
        raise TypeError("environment must be an Environment")
    if not isinstance(created_at, datetime) or created_at.tzinfo is None:
        raise ValueError("created_at must be timezone-aware")
    if created_at.utcoffset() is None:
        raise ValueError("created_at must have a valid UTC offset")


class _DuplicateFieldError(ValueError):
    def __init__(self, field_name: str) -> None:
        super().__init__(field_name)
        self.field_name = field_name


def _reject_duplicate_fields(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for field_name, value in pairs:
        if field_name in result:
            raise _DuplicateFieldError(field_name)
        result[field_name] = value
    return result


def _failure(
    code: MarkerValidationErrorCode,
    field_name: str | None = None,
) -> MarkerValidationFailure:
    return MarkerValidationFailure((MarkerValidationError(code, field_name),))


def _parse_uuid(
    value: str,
    error_code: MarkerValidationErrorCode,
) -> UUID | MarkerValidationError:
    if _CANONICAL_UUID_PATTERN.fullmatch(value) is None:
        return MarkerValidationError(error_code)
    try:
        parsed = UUID(value)
    except ValueError:
        return MarkerValidationError(error_code)
    if parsed.version != 4 or str(parsed) != value:
        return MarkerValidationError(error_code)
    return parsed


def _parse_created_at(value: str) -> datetime | None:
    if _RFC3339_PATTERN.fullmatch(value) is None:
        return None
    iso_value = f"{value[:-1]}+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(iso_value)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed


def parse_data_root_marker(data: bytes) -> DataRootMarker | MarkerValidationFailure:
    try:
        parsed_json = cast(
            object,
            json.loads(data, object_pairs_hook=_reject_duplicate_fields),
        )
    except _DuplicateFieldError as error:
        return _failure(
            MarkerValidationErrorCode.DUPLICATE_FIELD,
            error.field_name,
        )
    except (UnicodeDecodeError, json.JSONDecodeError):
        return _failure(MarkerValidationErrorCode.MALFORMED_JSON)

    if not isinstance(parsed_json, dict):
        return _failure(MarkerValidationErrorCode.JSON_ROOT_NOT_OBJECT)

    marker_object = cast(dict[str, object], parsed_json)
    schema_errors: list[MarkerValidationError] = []
    for field_name in _FIELD_NAMES:
        if field_name not in marker_object:
            schema_errors.append(
                MarkerValidationError(
                    MarkerValidationErrorCode.MISSING_FIELD,
                    field_name,
                )
            )
    for field_name in marker_object:
        if field_name not in _FIELD_NAME_SET:
            schema_errors.append(
                MarkerValidationError(
                    MarkerValidationErrorCode.UNKNOWN_FIELD,
                    field_name,
                )
            )
    if schema_errors:
        return MarkerValidationFailure(tuple(schema_errors))

    schema_version = marker_object["schema_version"]
    state_id = marker_object["state_id"]
    data_root_id = marker_object["data_root_id"]
    environment = marker_object["environment"]
    created_at = marker_object["created_at"]

    type_errors = tuple(
        MarkerValidationError(
            MarkerValidationErrorCode.INVALID_FIELD_TYPE,
            field_name,
        )
        for field_name, value, expected_type in (
            ("schema_version", schema_version, int),
            ("state_id", state_id, str),
            ("data_root_id", data_root_id, str),
            ("environment", environment, str),
            ("created_at", created_at, str),
        )
        if type(value) is not expected_type
    )
    if type_errors:
        return MarkerValidationFailure(type_errors)

    typed_schema_version = cast(int, schema_version)
    typed_state_id = cast(str, state_id)
    typed_data_root_id = cast(str, data_root_id)
    typed_environment = cast(str, environment)
    typed_created_at = cast(str, created_at)

    domain_errors: list[MarkerValidationError] = []
    if typed_schema_version != 1:
        domain_errors.append(
            MarkerValidationError(
                MarkerValidationErrorCode.UNSUPPORTED_SCHEMA_VERSION,
                "schema_version",
            )
        )

    parsed_state_id = _parse_uuid(
        typed_state_id,
        MarkerValidationErrorCode.INVALID_STATE_ID,
    )
    if isinstance(parsed_state_id, MarkerValidationError):
        domain_errors.append(MarkerValidationError(parsed_state_id.code, "state_id"))

    parsed_data_root_id = _parse_uuid(
        typed_data_root_id,
        MarkerValidationErrorCode.INVALID_DATA_ROOT_ID,
    )
    if isinstance(parsed_data_root_id, MarkerValidationError):
        domain_errors.append(
            MarkerValidationError(parsed_data_root_id.code, "data_root_id")
        )

    try:
        parsed_environment = Environment(typed_environment)
    except ValueError:
        parsed_environment = None
        domain_errors.append(
            MarkerValidationError(
                MarkerValidationErrorCode.INVALID_ENVIRONMENT,
                "environment",
            )
        )

    parsed_created_at = _parse_created_at(typed_created_at)
    if parsed_created_at is None:
        domain_errors.append(
            MarkerValidationError(
                MarkerValidationErrorCode.INVALID_CREATED_AT,
                "created_at",
            )
        )

    if domain_errors:
        return MarkerValidationFailure(tuple(domain_errors))

    return DataRootMarker(
        schema_version=typed_schema_version,
        state_id=cast(UUID, parsed_state_id),
        data_root_id=cast(UUID, parsed_data_root_id),
        environment=cast(Environment, parsed_environment),
        created_at=cast(datetime, parsed_created_at),
    )


def serialize_data_root_marker(marker: DataRootMarker) -> bytes:
    marker.__post_init__()
    created_at = marker.created_at.astimezone(UTC)
    timespec = "seconds" if created_at.microsecond == 0 else "microseconds"
    created_at_text = created_at.isoformat(timespec=timespec).removesuffix("+00:00") + "Z"
    document = {
        "schema_version": marker.schema_version,
        "state_id": str(marker.state_id),
        "data_root_id": str(marker.data_root_id),
        "environment": marker.environment.value,
        "created_at": created_at_text,
    }
    return (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
