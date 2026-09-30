import json
from datetime import UTC, datetime, timedelta, timezone
from uuid import UUID

import pytest

from argus.runtime.environment import Environment
from argus.runtime.runtime_identity import (
    RuntimeIdentity,
    RuntimeIdentityValidationError,
    RuntimeIdentityValidationErrorCode,
    RuntimeIdentityValidationFailure,
    parse_runtime_identity,
    serialize_runtime_identity,
)

STATE_ID = "12345678-1234-4234-9234-123456789abc"
DATA_ROOT_ID = "87654321-4321-4321-8321-cba987654321"


def identity_json_bytes(created_at: str) -> bytes:
    return json.dumps(
        {
            "schema_version": 1,
            "state_id": STATE_ID,
            "data_root_id": DATA_ROOT_ID,
            "environment": "TEST",
            "created_at": created_at,
        },
        separators=(",", ":"),
    ).encode()


@pytest.mark.parametrize(
    "created_at",
    [
        "2026-09-20T00:00:00+05:60",
        "2026-09-20T00:00:00-05:60",
        "2026-09-20T24:00:00Z",
        "2026-09-20T00:60:00Z",
        "2026-09-20T00:00:00+24:00",
    ],
)
def test_ri_l0_029_invalid_rfc3339_boundaries_are_rejected_without_repair(
    created_at: str,
) -> None:
    result = parse_runtime_identity(identity_json_bytes(created_at))

    assert result == RuntimeIdentityValidationFailure(
        errors=(
            RuntimeIdentityValidationError(
                RuntimeIdentityValidationErrorCode.INVALID_CREATED_AT,
                "created_at",
            ),
        )
    )


@pytest.mark.parametrize(
    "created_at",
    [
        "2026-09-20T23:59:59Z",
        "2026-09-20T00:00:00+23:59",
        "2026-09-20T00:00:00-23:59",
        "2026-09-20T00:00:00+05:59",
    ],
)
def test_ri_l0_030_valid_rfc3339_boundaries_remain_accepted(created_at: str) -> None:
    assert isinstance(parse_runtime_identity(identity_json_bytes(created_at)), RuntimeIdentity)


def test_ri_l0_031_pathologically_deep_json_is_a_typed_malformed_failure() -> None:
    depth = 100_000
    data = b'{"x":' + (b"[" * depth) + b"0" + (b"]" * depth) + b"}"

    result = parse_runtime_identity(data)

    assert result == RuntimeIdentityValidationFailure(
        errors=(
            RuntimeIdentityValidationError(
                RuntimeIdentityValidationErrorCode.MALFORMED_JSON,
            ),
        )
    )


@pytest.mark.parametrize(
    "created_at",
    [
        datetime.min.replace(tzinfo=timezone(timedelta(hours=1))),
        datetime.max.replace(tzinfo=timezone(-timedelta(hours=1))),
    ],
)
def test_ri_l0_032_serializer_maps_unrepresentable_utc_edges_to_value_error(
    created_at: datetime,
) -> None:
    identity = RuntimeIdentity(
        schema_version=1,
        state_id=UUID(STATE_ID),
        data_root_id=UUID(DATA_ROOT_ID),
        environment=Environment.TEST,
        created_at=created_at,
    )

    with pytest.raises(ValueError, match="canonical UTC range"):
        serialize_runtime_identity(identity)


@pytest.mark.parametrize(
    "created_at",
    [datetime.min.replace(tzinfo=UTC), datetime.max.replace(tzinfo=UTC)],
)
def test_ri_l0_033_serializer_supports_representable_datetime_range_edges(
    created_at: datetime,
) -> None:
    serialized = serialize_runtime_identity(
        RuntimeIdentity(
            schema_version=1,
            state_id=UUID(STATE_ID),
            data_root_id=UUID(DATA_ROOT_ID),
            environment=Environment.TEST,
            created_at=created_at,
        )
    )

    reparsed = parse_runtime_identity(serialized)
    assert isinstance(reparsed, RuntimeIdentity)
    assert reparsed.created_at == created_at


@pytest.mark.parametrize(
    ("data", "code", "field_name"),
    [
        pytest.param(
            b'{"schema_version":1,"schema_version":2',
            RuntimeIdentityValidationErrorCode.MALFORMED_JSON,
            None,
            id="top-level-duplicate-not-reached-before-truncation",
        ),
        pytest.param(
            b'{"unknown":{"a":1,"a":2}',
            RuntimeIdentityValidationErrorCode.DUPLICATE_FIELD,
            "a",
            id="nested-duplicate-detected-before-outer-truncation",
        ),
        pytest.param(
            b'{"unknown":tru,"a":1,"a":2}',
            RuntimeIdentityValidationErrorCode.MALFORMED_JSON,
            None,
            id="malformed-detected-before-later-duplicate",
        ),
    ],
)
def test_ri_l0_034_returns_first_defect_detected_by_validation_pipeline(
    data: bytes,
    code: RuntimeIdentityValidationErrorCode,
    field_name: str | None,
) -> None:
    result = parse_runtime_identity(data)

    assert result == RuntimeIdentityValidationFailure(
        errors=(RuntimeIdentityValidationError(code, field_name),)
    )
