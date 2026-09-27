from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

import pytest

from argus.runtime.data_root_marker import (
    DataRootMarker,
    MarkerValidationErrorCode,
    MarkerValidationFailure,
    parse_data_root_marker,
)
from argus.runtime.environment import Environment

STATE_ID = UUID("12345678-1234-4234-9234-123456789abc")
DATA_ROOT_ID = UUID("87654321-4321-4321-8321-cba987654321")
CREATED_AT = datetime(2026, 9, 12, 5, 0, tzinfo=UTC)


def test_data_root_marker_can_be_created() -> None:
    marker = DataRootMarker(
        schema_version=1,
        state_id=STATE_ID,
        data_root_id=DATA_ROOT_ID,
        environment=Environment.TEST,
        created_at=CREATED_AT,
    )

    assert marker.schema_version == 1
    assert marker.state_id == STATE_ID
    assert marker.data_root_id == DATA_ROOT_ID
    assert marker.environment is Environment.TEST
    assert marker.created_at == CREATED_AT


@pytest.mark.parametrize(
    "field_name",
    [
        "state_id",
        "data_root_id",
        "created_at",
    ],
)
def test_data_root_marker_rejects_invalid_required_fields(
    field_name: Literal["state_id", "data_root_id", "created_at"],
) -> None:
    non_v4_uuid = UUID("12345678-1234-1234-9234-123456789abc")
    state_id = non_v4_uuid if field_name == "state_id" else STATE_ID
    data_root_id = non_v4_uuid if field_name == "data_root_id" else DATA_ROOT_ID
    created_at = (
        CREATED_AT.replace(tzinfo=None)
        if field_name == "created_at"
        else CREATED_AT
    )

    with pytest.raises(ValueError):
        DataRootMarker(
            schema_version=1,
            state_id=state_id,
            data_root_id=data_root_id,
            environment=Environment.TEST,
            created_at=created_at,
        )


def test_created_at_rejects_unicode_decimal_digits() -> None:
    data = (
        '{"schema_version":1,'
        '"state_id":"12345678-1234-4234-9234-123456789abc",'
        '"data_root_id":"87654321-4321-4321-8321-cba987654321",'
        '"environment":"TEST",'
        '"created_at":"２０２６-09-14T01:02:03Z"}'
    ).encode()

    result = parse_data_root_marker(data)

    assert isinstance(result, MarkerValidationFailure)
    assert MarkerValidationErrorCode.INVALID_CREATED_AT in {
        error.code
        for error in result.errors
        if error.field_name == "created_at"
    }
