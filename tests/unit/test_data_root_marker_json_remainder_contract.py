import json
from datetime import UTC, datetime, timedelta, timezone
from uuid import UUID

import pytest

from argus.runtime.data_root_marker import (
    DataRootMarker,
    MarkerValidationError,
    MarkerValidationErrorCode,
    MarkerValidationFailure,
    parse_data_root_marker,
)
from argus.runtime.environment import Environment

STATE_ID = "12345678-1234-4234-9234-123456789abc"
DATA_ROOT_ID = "87654321-4321-4321-8321-cba987654321"
CREATED_AT = "2026-09-14T01:02:03Z"


def marker_json_bytes(
    *,
    schema_version: object = 1,
    state_id: object = STATE_ID,
    data_root_id: object = DATA_ROOT_ID,
    environment: object = "TEST",
    created_at: object = CREATED_AT,
) -> bytes:
    return json.dumps(
        {
            "schema_version": schema_version,
            "state_id": state_id,
            "data_root_id": data_root_id,
            "environment": environment,
            "created_at": created_at,
        }
    ).encode()


def assert_single_validation_error(
    result: DataRootMarker | MarkerValidationFailure,
    code: MarkerValidationErrorCode,
    field_name: str | None,
) -> None:
    assert isinstance(result, MarkerValidationFailure)
    assert result.errors == (MarkerValidationError(code, field_name),)


@pytest.mark.parametrize("data", [b"[]", b"null", b'"marker"', b"1"])
def test_eb_l0_005_json_root_non_object(data: bytes) -> None:
    result = parse_data_root_marker(data)

    assert_single_validation_error(
        result,
        MarkerValidationErrorCode.JSON_ROOT_NOT_OBJECT,
        None,
    )


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("schema_version", "1"),
        ("state_id", 1),
        ("data_root_id", None),
        ("environment", ["TEST"]),
        ("created_at", 20260914),
    ],
)
def test_eb_l0_006_invalid_field_type(
    field_name: str,
    invalid_value: object,
) -> None:
    values: dict[str, object] = {
        "schema_version": 1,
        "state_id": STATE_ID,
        "data_root_id": DATA_ROOT_ID,
        "environment": "TEST",
        "created_at": CREATED_AT,
    }
    values[field_name] = invalid_value

    result = parse_data_root_marker(
        marker_json_bytes(
            schema_version=values["schema_version"],
            state_id=values["state_id"],
            data_root_id=values["data_root_id"],
            environment=values["environment"],
            created_at=values["created_at"],
        )
    )

    assert_single_validation_error(
        result,
        MarkerValidationErrorCode.INVALID_FIELD_TYPE,
        field_name,
    )


@pytest.mark.parametrize("schema_version", [0, 2, -1])
def test_eb_l0_007_unsupported_schema_version(schema_version: int) -> None:
    result = parse_data_root_marker(
        marker_json_bytes(schema_version=schema_version)
    )

    assert_single_validation_error(
        result,
        MarkerValidationErrorCode.UNSUPPORTED_SCHEMA_VERSION,
        "schema_version",
    )


def test_eb_l0_009_canonical_uuid_v4_is_accepted() -> None:
    result = parse_data_root_marker(marker_json_bytes())

    assert isinstance(result, DataRootMarker)
    assert result.state_id == UUID(STATE_ID)
    assert result.state_id.version == 4
    assert result.data_root_id == UUID(DATA_ROOT_ID)
    assert result.data_root_id.version == 4


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "expected_code"),
    [
        (
            "state_id",
            "12345678-1234-1234-9234-123456789abc",
            MarkerValidationErrorCode.INVALID_STATE_ID,
        ),
        (
            "data_root_id",
            "87654321-4321-1321-8321-cba987654321",
            MarkerValidationErrorCode.INVALID_DATA_ROOT_ID,
        ),
    ],
)
def test_eb_l0_010_non_v4_uuid_is_rejected(
    field_name: str,
    invalid_value: str,
    expected_code: MarkerValidationErrorCode,
) -> None:
    state_id = invalid_value if field_name == "state_id" else STATE_ID
    data_root_id = invalid_value if field_name == "data_root_id" else DATA_ROOT_ID

    result = parse_data_root_marker(
        marker_json_bytes(state_id=state_id, data_root_id=data_root_id)
    )

    assert_single_validation_error(result, expected_code, field_name)


@pytest.mark.parametrize("environment", ["PROD", "test", ""])
def test_eb_l0_012_invalid_environment_is_rejected(environment: str) -> None:
    result = parse_data_root_marker(marker_json_bytes(environment=environment))

    assert_single_validation_error(
        result,
        MarkerValidationErrorCode.INVALID_ENVIRONMENT,
        "environment",
    )


@pytest.mark.parametrize(
    ("created_at", "expected"),
    [
        ("2026-09-14T01:02:03Z", datetime(2026, 9, 14, 1, 2, 3, tzinfo=UTC)),
        (
            "2026-09-14T01:02:03.1Z",
            datetime(2026, 9, 14, 1, 2, 3, 100000, tzinfo=UTC),
        ),
        (
            "2026-09-14T01:02:03.123456Z",
            datetime(2026, 9, 14, 1, 2, 3, 123456, tzinfo=UTC),
        ),
        (
            "2026-09-14T10:02:03+09:00",
            datetime(2026, 9, 14, 10, 2, 3, tzinfo=timezone(timedelta(hours=9))),
        ),
        (
            "2026-09-13T19:32:03.1-05:30",
            datetime(
                2026,
                9,
                13,
                19,
                32,
                3,
                100000,
                tzinfo=timezone(-timedelta(hours=5, minutes=30)),
            ),
        ),
        (
            "2026-09-14T01:02:03.123456+00:00",
            datetime(2026, 9, 14, 1, 2, 3, 123456, tzinfo=UTC),
        ),
    ],
)
def test_eb_l0_013_accepted_rfc3339_variants(
    created_at: str,
    expected: datetime,
) -> None:
    result = parse_data_root_marker(marker_json_bytes(created_at=created_at))

    assert isinstance(result, DataRootMarker)
    assert result.created_at == expected
    assert result.environment is Environment.TEST
