import json
from datetime import UTC, datetime
from uuid import UUID

import pytest

from argus.runtime.data_root_marker import (
    DataRootMarker,
    MarkerValidationErrorCode,
    MarkerValidationFailure,
    parse_data_root_marker,
    serialize_data_root_marker,
)
from argus.runtime.environment import Environment

STATE_ID = "12345678-1234-4234-9234-123456789abc"
DATA_ROOT_ID = "87654321-4321-4321-8321-cba987654321"
CREATED_AT = "2026-09-14T01:02:03Z"


def marker_json_bytes(
    *,
    schema_version: int | bool = 1,
    state_id: str = STATE_ID,
    data_root_id: str = DATA_ROOT_ID,
    environment: str = "TEST",
    created_at: str = CREATED_AT,
) -> bytes:
    return json.dumps(
        {
            "schema_version": schema_version,
            "state_id": state_id,
            "data_root_id": data_root_id,
            "environment": environment,
            "created_at": created_at,
        }
    ).encode("utf-8")


def assert_validation_error(
    result: DataRootMarker | MarkerValidationFailure,
    expected_code: MarkerValidationErrorCode,
    expected_field_name: str,
) -> None:
    assert isinstance(result, MarkerValidationFailure)
    assert result.errors
    assert any(
        error.code is expected_code and error.field_name == expected_field_name
        for error in result.errors
    )


def test_eb_l0_001_valid_marker() -> None:
    result = parse_data_root_marker(marker_json_bytes())

    assert isinstance(result, DataRootMarker)
    assert result.schema_version == 1
    assert result.state_id == UUID(STATE_ID)
    assert result.data_root_id == UUID(DATA_ROOT_ID)
    assert result.environment is Environment.TEST
    assert result.created_at == datetime(2026, 9, 14, 1, 2, 3, tzinfo=UTC)


def test_eb_l0_002_missing_required_field() -> None:
    data = (
        b'{"schema_version":1,'
        b'"state_id":"12345678-1234-4234-9234-123456789abc",'
        b'"environment":"TEST",'
        b'"created_at":"2026-09-14T01:02:03Z"}'
    )

    result = parse_data_root_marker(data)

    assert_validation_error(
        result,
        MarkerValidationErrorCode.MISSING_FIELD,
        "data_root_id",
    )


def test_eb_l0_003_unknown_field() -> None:
    data = (
        b'{"schema_version":1,'
        b'"state_id":"12345678-1234-4234-9234-123456789abc",'
        b'"data_root_id":"87654321-4321-4321-8321-cba987654321",'
        b'"environment":"TEST",'
        b'"created_at":"2026-09-14T01:02:03Z",'
        b'"unexpected":"must-not-be-ignored"}'
    )

    result = parse_data_root_marker(data)

    assert_validation_error(
        result,
        MarkerValidationErrorCode.UNKNOWN_FIELD,
        "unexpected",
    )


def test_eb_l0_004_duplicate_field() -> None:
    data = (
        b'{"schema_version":1,'
        b'"state_id":"12345678-1234-4234-9234-123456789abc",'
        b'"state_id":"aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",'
        b'"data_root_id":"87654321-4321-4321-8321-cba987654321",'
        b'"environment":"TEST",'
        b'"created_at":"2026-09-14T01:02:03Z"}'
    )

    result = parse_data_root_marker(data)

    assert_validation_error(
        result,
        MarkerValidationErrorCode.DUPLICATE_FIELD,
        "state_id",
    )


def test_eb_l0_008_boolean_schema_version_is_rejected() -> None:
    result = parse_data_root_marker(marker_json_bytes(schema_version=True))

    assert_validation_error(
        result,
        MarkerValidationErrorCode.INVALID_FIELD_TYPE,
        "schema_version",
    )


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "expected_code"),
    [
        (
            "state_id",
            "12345678-1234-4234-9234-123456789ABC",
            MarkerValidationErrorCode.INVALID_STATE_ID,
        ),
        (
            "state_id",
            "{12345678-1234-4234-9234-123456789abc}",
            MarkerValidationErrorCode.INVALID_STATE_ID,
        ),
        (
            "state_id",
            "urn:uuid:12345678-1234-4234-9234-123456789abc",
            MarkerValidationErrorCode.INVALID_STATE_ID,
        ),
        (
            "state_id",
            "12345678123442349234123456789abc",
            MarkerValidationErrorCode.INVALID_STATE_ID,
        ),
        (
            "data_root_id",
            "87654321-4321-4321-8321-CBA987654321",
            MarkerValidationErrorCode.INVALID_DATA_ROOT_ID,
        ),
        (
            "data_root_id",
            "{87654321-4321-4321-8321-cba987654321}",
            MarkerValidationErrorCode.INVALID_DATA_ROOT_ID,
        ),
        (
            "data_root_id",
            "urn:uuid:87654321-4321-4321-8321-cba987654321",
            MarkerValidationErrorCode.INVALID_DATA_ROOT_ID,
        ),
        (
            "data_root_id",
            "87654321432143218321cba987654321",
            MarkerValidationErrorCode.INVALID_DATA_ROOT_ID,
        ),
    ],
)
def test_eb_l0_011_non_canonical_uuid_is_rejected(
    field_name: str,
    invalid_value: str,
    expected_code: MarkerValidationErrorCode,
) -> None:
    state_id = invalid_value if field_name == "state_id" else STATE_ID
    data_root_id = invalid_value if field_name == "data_root_id" else DATA_ROOT_ID

    result = parse_data_root_marker(
        marker_json_bytes(state_id=state_id, data_root_id=data_root_id)
    )

    assert_validation_error(result, expected_code, field_name)


@pytest.mark.parametrize(
    "invalid_created_at",
    [
        "2026-09-14T01:02:03",
        "2026-09-14T01:02:03+09:00:00",
        "2026-09-14T01:02:60Z",
        "2026-09-14 01:02:03Z",
        "2026-09-14T01:02:03.1234567Z",
    ],
)
def test_eb_l0_014_rejected_rfc3339_forms(invalid_created_at: str) -> None:
    result = parse_data_root_marker(marker_json_bytes(created_at=invalid_created_at))

    assert_validation_error(
        result,
        MarkerValidationErrorCode.INVALID_CREATED_AT,
        "created_at",
    )


def test_eb_l0_015_deterministic_serialization() -> None:
    parsed = parse_data_root_marker(marker_json_bytes())
    assert isinstance(parsed, DataRootMarker)

    serialized = serialize_data_root_marker(parsed)

    expected = (
        b'{\n'
        b'  "schema_version": 1,\n'
        b'  "state_id": "12345678-1234-4234-9234-123456789abc",\n'
        b'  "data_root_id": "87654321-4321-4321-8321-cba987654321",\n'
        b'  "environment": "TEST",\n'
        b'  "created_at": "2026-09-14T01:02:03Z"\n'
        b'}\n'
    )
    assert serialized == expected
    assert serialized.decode("utf-8")
    assert not serialized.startswith(b"\xef\xbb\xbf")
    assert b"\r" not in serialized
    assert serialized.endswith(b"\n")


def test_eb_l0_016_utc_normalization() -> None:
    parsed = parse_data_root_marker(
        marker_json_bytes(created_at="2026-09-14T10:02:03.123456+09:00")
    )
    assert isinstance(parsed, DataRootMarker)

    serialized = serialize_data_root_marker(parsed)

    assert b'"created_at": "2026-09-14T01:02:03.123456Z"' in serialized
    assert b"+00:00" not in serialized
    assert b"+09:00" not in serialized
