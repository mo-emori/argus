import builtins
import json
import os
import socket
from datetime import UTC, datetime, timedelta, timezone
from typing import Any, cast
from uuid import UUID

import argus.runtime.runtime_identity as runtime_identity_module
import pytest
from argus.runtime.runtime_identity import (
    RuntimeIdentity,
    RuntimeIdentityValidationError,
    RuntimeIdentityValidationErrorCode,
    RuntimeIdentityValidationFailure,
    parse_runtime_identity,
    serialize_runtime_identity,
)

from argus.runtime.environment import Environment

STATE_ID = "12345678-1234-4234-9234-123456789abc"
DATA_ROOT_ID = "87654321-4321-4321-8321-cba987654321"
CREATED_AT = "2026-09-20T00:00:00Z"
CANONICAL_BYTES = (
    b"{\n"
    b'  "schema_version": 1,\n'
    b'  "state_id": "12345678-1234-4234-9234-123456789abc",\n'
    b'  "data_root_id": "87654321-4321-4321-8321-cba987654321",\n'
    b'  "environment": "TEST",\n'
    b'  "created_at": "2026-09-20T00:00:00Z"\n'
    b"}\n"
)


def identity_json_bytes(**overrides: object) -> bytes:
    values: dict[str, object] = {
        "schema_version": 1,
        "state_id": STATE_ID,
        "data_root_id": DATA_ROOT_ID,
        "environment": "TEST",
        "created_at": CREATED_AT,
    }
    values.update(overrides)
    return json.dumps(values, ensure_ascii=False, separators=(",", ":")).encode()


def assert_single_error(
    result: RuntimeIdentity | RuntimeIdentityValidationFailure,
    code: RuntimeIdentityValidationErrorCode,
    field_name: str | None,
) -> None:
    assert isinstance(result, RuntimeIdentityValidationFailure)
    assert result.errors == (RuntimeIdentityValidationError(code, field_name),)


def test_ri_l0_001_valid_canonical_document() -> None:
    result = parse_runtime_identity(CANONICAL_BYTES)

    assert isinstance(result, RuntimeIdentity)
    assert result == RuntimeIdentity(
        schema_version=1,
        state_id=UUID(STATE_ID),
        data_root_id=UUID(DATA_ROOT_ID),
        environment=Environment.TEST,
        created_at=datetime(2026, 9, 20, tzinfo=UTC),
    )


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(b"\xff", id="invalid-utf8"),
        pytest.param(b"\xef\xbb\xbf{}", id="utf8-bom"),
        pytest.param(b'{"schema_version":', id="truncated"),
        pytest.param(CANONICAL_BYTES + b"true", id="trailing-data"),
        pytest.param(identity_json_bytes(schema_version=float("nan")), id="nan"),
        pytest.param(identity_json_bytes(schema_version=float("inf")), id="infinity"),
        pytest.param(identity_json_bytes(schema_version=float("-inf")), id="minus-infinity"),
    ],
)
def test_ri_l0_002_malformed_encoding_and_non_standard_json(data: bytes) -> None:
    assert_single_error(
        parse_runtime_identity(data),
        RuntimeIdentityValidationErrorCode.MALFORMED_JSON,
        None,
    )


@pytest.mark.parametrize("data", [b"[]", b'"identity"', b"1", b"true", b"null"])
def test_ri_l0_003_json_root_must_be_object(data: bytes) -> None:
    assert_single_error(
        parse_runtime_identity(data),
        RuntimeIdentityValidationErrorCode.JSON_ROOT_NOT_OBJECT,
        None,
    )


@pytest.mark.parametrize(
    "field_name",
    ["schema_version", "state_id", "data_root_id", "environment", "created_at"],
)
def test_ri_l0_004_every_field_is_required(field_name: str) -> None:
    document = json.loads(CANONICAL_BYTES)
    del document[field_name]

    assert_single_error(
        parse_runtime_identity(json.dumps(document).encode()),
        RuntimeIdentityValidationErrorCode.MISSING_FIELD,
        field_name,
    )


@pytest.mark.parametrize(
    ("unknown_fields", "expected_names"),
    [
        ('"extra":1', ("extra",)),
        ('"未知":1', ("未知",)),
        ('"first":1,"last":2', ("first", "last")),
        ('"未知":1,"追加":2', ("未知", "追加")),
        ('"first":1,"未知":2,"last":3', ("first", "未知", "last")),
    ],
)
def test_ri_l0_005_unknown_fields_preserve_encounter_order(
    unknown_fields: str,
    expected_names: tuple[str, ...],
) -> None:
    data = CANONICAL_BYTES.rstrip()[:-1] + f",{unknown_fields}}}".encode()

    result = parse_runtime_identity(data)

    assert isinstance(result, RuntimeIdentityValidationFailure)
    assert result.errors == tuple(
        RuntimeIdentityValidationError(
            RuntimeIdentityValidationErrorCode.UNKNOWN_FIELD,
            name,
        )
        for name in expected_names
    )


@pytest.mark.parametrize(
    ("duplicate_key", "decoded_key"),
    [
        ('schema_version', "schema_version"),
        ('state_\\u0069d', "state_id"),
        ('data_root_id', "data_root_id"),
        ('environment', "environment"),
        ('created_at', "created_at"),
    ],
)
def test_ri_l0_006_each_required_duplicate_decoded_key_is_terminal(
    duplicate_key: str,
    decoded_key: str,
) -> None:
    data = CANONICAL_BYTES.rstrip()[:-1] + f',"{duplicate_key}":null}}'.encode()

    assert_single_error(
        parse_runtime_identity(data),
        RuntimeIdentityValidationErrorCode.DUPLICATE_FIELD,
        decoded_key,
    )


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        pytest.param("schema_version", "1", id="schema-string"),
        pytest.param("schema_version", 1.5, id="schema-float"),
        pytest.param("state_id", 1, id="state-integer"),
        pytest.param("state_id", {}, id="state-object"),
        pytest.param("data_root_id", [], id="data-root-array"),
        pytest.param("environment", None, id="environment-null"),
        pytest.param("created_at", False, id="created-at-boolean"),
    ],
)
def test_ri_l0_007_exact_field_types_no_coercion(
    field_name: str,
    invalid_value: object,
) -> None:
    assert_single_error(
        parse_runtime_identity(identity_json_bytes(**{field_name: invalid_value})),
        RuntimeIdentityValidationErrorCode.INVALID_FIELD_TYPE,
        field_name,
    )


@pytest.mark.parametrize("schema_version", [True, False])
def test_ri_l0_008_boolean_is_not_an_integer(schema_version: bool) -> None:
    assert_single_error(
        parse_runtime_identity(identity_json_bytes(schema_version=schema_version)),
        RuntimeIdentityValidationErrorCode.INVALID_FIELD_TYPE,
        "schema_version",
    )


@pytest.mark.parametrize("schema_version", [0, 2, -1])
def test_ri_l0_009_only_schema_version_one_is_supported(schema_version: int) -> None:
    assert_single_error(
        parse_runtime_identity(identity_json_bytes(schema_version=schema_version)),
        RuntimeIdentityValidationErrorCode.UNSUPPORTED_SCHEMA_VERSION,
        "schema_version",
    )


def test_ri_l0_010_canonical_uuid_v4_values_are_accepted() -> None:
    result = parse_runtime_identity(identity_json_bytes())

    assert isinstance(result, RuntimeIdentity)
    assert result.state_id == UUID(STATE_ID)
    assert result.state_id.version == 4
    assert result.data_root_id == UUID(DATA_ROOT_ID)
    assert result.data_root_id.version == 4


INVALID_STATE_IDS = [
    "12345678-1234-4234-9234-123456789ABC",
    "{12345678-1234-4234-9234-123456789abc}",
    "urn:uuid:12345678-1234-4234-9234-123456789abc",
    "12345678123442349234123456789abc",
    f" {STATE_ID}",
    f"{STATE_ID} ",
    "12345678-1234-1234-9234-123456789abc",
    "not-a-uuid",
]


@pytest.mark.parametrize("state_id", INVALID_STATE_IDS)
def test_ri_l0_011_invalid_state_uuid_is_rejected_without_normalization(
    state_id: str,
) -> None:
    assert_single_error(
        parse_runtime_identity(identity_json_bytes(state_id=state_id)),
        RuntimeIdentityValidationErrorCode.INVALID_STATE_ID,
        "state_id",
    )


@pytest.mark.parametrize(
    "data_root_id",
    [
        "87654321-4321-4321-8321-CBA987654321",
        "{87654321-4321-4321-8321-cba987654321}",
        "urn:uuid:87654321-4321-4321-8321-cba987654321",
        "87654321432143218321cba987654321",
        f" {DATA_ROOT_ID}",
        f"{DATA_ROOT_ID} ",
        "87654321-4321-1321-8321-cba987654321",
        "not-a-uuid",
    ],
)
def test_ri_l0_012_invalid_data_root_uuid_is_rejected_without_normalization(
    data_root_id: str,
) -> None:
    assert_single_error(
        parse_runtime_identity(identity_json_bytes(data_root_id=data_root_id)),
        RuntimeIdentityValidationErrorCode.INVALID_DATA_ROOT_ID,
        "data_root_id",
    )


@pytest.mark.parametrize(
    ("environment", "expected"),
    [("TEST", Environment.TEST), ("PAPER", Environment.PAPER), ("LIVE", Environment.LIVE)],
)
def test_ri_l0_013_environment_closed_set(
    environment: str,
    expected: Environment,
) -> None:
    result = parse_runtime_identity(identity_json_bytes(environment=environment))

    assert isinstance(result, RuntimeIdentity)
    assert result.environment is expected


@pytest.mark.parametrize("environment", ["test", "PROD", "", " TEST", "TEST "])
def test_ri_l0_014_invalid_environment_is_rejected(environment: str) -> None:
    assert_single_error(
        parse_runtime_identity(identity_json_bytes(environment=environment)),
        RuntimeIdentityValidationErrorCode.INVALID_ENVIRONMENT,
        "environment",
    )


@pytest.mark.parametrize(
    ("created_at", "expected"),
    [
        ("2026-09-20T00:00:00Z", datetime(2026, 9, 20, tzinfo=UTC)),
        ("2026-09-20T00:00:00.0Z", datetime(2026, 9, 20, tzinfo=UTC)),
        (
            "2026-09-20T00:00:00.1Z",
            datetime(2026, 9, 20, microsecond=100000, tzinfo=UTC),
        ),
        (
            "2026-09-20T00:00:00.123456Z",
            datetime(2026, 9, 20, microsecond=123456, tzinfo=UTC),
        ),
        (
            "2026-09-20T09:00:00+09:00",
            datetime(2026, 9, 20, 9, tzinfo=timezone(timedelta(hours=9))),
        ),
        (
            "2026-09-19T18:30:00.1-05:30",
            datetime(
                2026,
                9,
                19,
                18,
                30,
                microsecond=100000,
                tzinfo=timezone(-timedelta(hours=5, minutes=30)),
            ),
        ),
    ],
)
def test_ri_l0_015_accepted_rfc3339_variants(
    created_at: str,
    expected: datetime,
) -> None:
    result = parse_runtime_identity(identity_json_bytes(created_at=created_at))

    assert isinstance(result, RuntimeIdentity)
    assert result.created_at == expected
    assert result.created_at.utcoffset() is not None


@pytest.mark.parametrize(
    "created_at",
    [
        "2026-09-20T00:00:00",
        "2026-09-20T00:00:00+09:00:00",
        "2026-09-20T00:00:60Z",
        "2026-09-20 00:00:00Z",
        "2026-09-20T00:00:00.1234567Z",
        "２０２６-09-20T00:00:00Z",
        "2026-02-30T00:00:00Z",
        " 2026-09-20T00:00:00Z",
        "2026-09-20T00:00:00Z ",
    ],
)
def test_ri_l0_016_rejected_rfc3339_forms(created_at: str) -> None:
    assert_single_error(
        parse_runtime_identity(identity_json_bytes(created_at=created_at)),
        RuntimeIdentityValidationErrorCode.INVALID_CREATED_AT,
        "created_at",
    )


def test_ri_l0_017_schema_errors_have_deterministic_order() -> None:
    data = b'{"unknown_z":0,"environment":"TEST","unknown_a":1}'

    result = parse_runtime_identity(data)

    assert isinstance(result, RuntimeIdentityValidationFailure)
    assert result.errors == (
        RuntimeIdentityValidationError(
            RuntimeIdentityValidationErrorCode.MISSING_FIELD, "schema_version"
        ),
        RuntimeIdentityValidationError(
            RuntimeIdentityValidationErrorCode.MISSING_FIELD, "state_id"
        ),
        RuntimeIdentityValidationError(
            RuntimeIdentityValidationErrorCode.MISSING_FIELD, "data_root_id"
        ),
        RuntimeIdentityValidationError(
            RuntimeIdentityValidationErrorCode.MISSING_FIELD, "created_at"
        ),
        RuntimeIdentityValidationError(
            RuntimeIdentityValidationErrorCode.UNKNOWN_FIELD, "unknown_z"
        ),
        RuntimeIdentityValidationError(
            RuntimeIdentityValidationErrorCode.UNKNOWN_FIELD, "unknown_a"
        ),
    )


def test_ri_l0_018_type_errors_have_canonical_order_and_stop_domain_validation() -> None:
    result = parse_runtime_identity(
        identity_json_bytes(
            schema_version="unsupported",
            state_id=1,
            data_root_id=None,
            environment=[],
            created_at={},
        )
    )

    assert isinstance(result, RuntimeIdentityValidationFailure)
    assert result.errors == tuple(
        RuntimeIdentityValidationError(
            RuntimeIdentityValidationErrorCode.INVALID_FIELD_TYPE,
            field_name,
        )
        for field_name in (
            "schema_version",
            "state_id",
            "data_root_id",
            "environment",
            "created_at",
        )
    )


def test_ri_l0_018_any_type_error_prevents_domain_phase() -> None:
    result = parse_runtime_identity(
        identity_json_bytes(
            schema_version=2,
            state_id=1,
            data_root_id="invalid-data-root",
            environment="PROD",
            created_at="invalid-created-at",
        )
    )

    assert_single_error(
        result,
        RuntimeIdentityValidationErrorCode.INVALID_FIELD_TYPE,
        "state_id",
    )


def test_ri_l0_019_domain_errors_have_canonical_order() -> None:
    result = parse_runtime_identity(
        identity_json_bytes(
            schema_version=2,
            state_id="invalid-state",
            data_root_id="invalid-data-root",
            environment="PROD",
            created_at="invalid-created-at",
        )
    )

    assert isinstance(result, RuntimeIdentityValidationFailure)
    assert result.errors == tuple(
        RuntimeIdentityValidationError(code, field_name)
        for code, field_name in (
            (
                RuntimeIdentityValidationErrorCode.UNSUPPORTED_SCHEMA_VERSION,
                "schema_version",
            ),
            (RuntimeIdentityValidationErrorCode.INVALID_STATE_ID, "state_id"),
            (RuntimeIdentityValidationErrorCode.INVALID_DATA_ROOT_ID, "data_root_id"),
            (RuntimeIdentityValidationErrorCode.INVALID_ENVIRONMENT, "environment"),
            (RuntimeIdentityValidationErrorCode.INVALID_CREATED_AT, "created_at"),
        )
    )


def test_ri_l0_020_first_duplicate_has_structural_precedence() -> None:
    data = (
        b'{"schema_version":"wrong-type","schema_version":2,'
        b'"state_id":"invalid","state_id":"also-invalid","unknown":true}'
    )

    assert_single_error(
        parse_runtime_identity(data),
        RuntimeIdentityValidationErrorCode.DUPLICATE_FIELD,
        "schema_version",
    )


@pytest.mark.parametrize("whitespace", [b" ", b"\t", b"\r", b"\n", b" \t\r\n"])
def test_ri_l0_021_rfc8259_whitespace_around_root_is_accepted(
    whitespace: bytes,
) -> None:
    result = parse_runtime_identity(whitespace + CANONICAL_BYTES + whitespace)

    assert isinstance(result, RuntimeIdentity)
    assert result.state_id == UUID(STATE_ID)


@pytest.mark.parametrize(
    ("overrides", "code", "field_name"),
    [
        (
            {"state_id": f" {STATE_ID}"},
            RuntimeIdentityValidationErrorCode.INVALID_STATE_ID,
            "state_id",
        ),
        (
            {"environment": "test"},
            RuntimeIdentityValidationErrorCode.INVALID_ENVIRONMENT,
            "environment",
        ),
        (
            {"created_at": "2026-09-20T00:00:00"},
            RuntimeIdentityValidationErrorCode.INVALID_CREATED_AT,
            "created_at",
        ),
    ],
)
def test_ri_l0_022_field_values_are_not_normalized(
    overrides: dict[str, object],
    code: RuntimeIdentityValidationErrorCode,
    field_name: str,
) -> None:
    assert_single_error(parse_runtime_identity(identity_json_bytes(**overrides)), code, field_name)


def test_ri_l0_023_exact_serialization_bytes() -> None:
    identity = RuntimeIdentity(
        schema_version=1,
        state_id=UUID(STATE_ID),
        data_root_id=UUID(DATA_ROOT_ID),
        environment=Environment.TEST,
        created_at=datetime(2026, 9, 20, tzinfo=UTC),
    )

    serialized = serialize_runtime_identity(identity)

    assert serialized == CANONICAL_BYTES
    assert not serialized.startswith(b"\xef\xbb\xbf")
    assert b"\r" not in serialized
    assert serialized.endswith(b"\n")


@pytest.mark.parametrize(
    ("created_at", "serialized_created_at"),
    [
        (datetime(2026, 9, 20, 9, tzinfo=timezone(timedelta(hours=9))), CREATED_AT),
        (
            datetime(
                2026,
                9,
                20,
                9,
                microsecond=100000,
                tzinfo=timezone(timedelta(hours=9)),
            ),
            "2026-09-20T00:00:00.100000Z",
        ),
        (
            datetime(
                2026,
                9,
                20,
                9,
                microsecond=1,
                tzinfo=timezone(timedelta(hours=9)),
            ),
            "2026-09-20T00:00:00.000001Z",
        ),
        (
            datetime(
                2026,
                9,
                20,
                9,
                microsecond=123456,
                tzinfo=timezone(timedelta(hours=9)),
            ),
            "2026-09-20T00:00:00.123456Z",
        ),
    ],
)
def test_ri_l0_024_serialization_normalizes_utc_and_fraction(
    created_at: datetime,
    serialized_created_at: str,
) -> None:
    identity = RuntimeIdentity(
        schema_version=1,
        state_id=UUID(STATE_ID),
        data_root_id=UUID(DATA_ROOT_ID),
        environment=Environment.TEST,
        created_at=created_at,
    )

    serialized = serialize_runtime_identity(identity)

    expected = CANONICAL_BYTES.replace(
        b'"created_at": "2026-09-20T00:00:00Z"',
        f'"created_at": "{serialized_created_at}"'.encode(),
    )
    assert serialized == expected


@pytest.mark.parametrize(
    ("environment", "created_at", "canonical_created_at"),
    [
        ("TEST", "2026-09-20T00:00:00Z", "2026-09-20T00:00:00Z"),
        ("TEST", "2026-09-20T00:00:00.0Z", "2026-09-20T00:00:00Z"),
        ("TEST", "2026-09-20T00:00:00.1Z", "2026-09-20T00:00:00.100000Z"),
        ("TEST", "2026-09-20T00:00:00.123456Z", "2026-09-20T00:00:00.123456Z"),
        ("PAPER", "2026-09-20T09:00:00+09:00", "2026-09-20T00:00:00Z"),
        (
            "LIVE",
            "2026-09-19T18:30:00.123456-05:30",
            "2026-09-20T00:00:00.123456Z",
        ),
    ],
)
def test_ri_l0_025_accepted_variants_round_trip_to_canonical_bytes(
    environment: str,
    created_at: str,
    canonical_created_at: str,
) -> None:
    parsed = parse_runtime_identity(
        identity_json_bytes(environment=environment, created_at=created_at)
    )
    assert isinstance(parsed, RuntimeIdentity)

    serialized = serialize_runtime_identity(parsed)
    reparsed = parse_runtime_identity(serialized)
    expected = CANONICAL_BYTES.replace(
        b'"environment": "TEST"', f'"environment": "{environment}"'.encode()
    )
    expected = expected.replace(
        b'"created_at": "2026-09-20T00:00:00Z"',
        f'"created_at": "{canonical_created_at}"'.encode(),
    )

    assert reparsed == parsed
    assert serialized == serialize_runtime_identity(parsed) == expected


def invalid_identity(**overrides: object) -> RuntimeIdentity:
    values: dict[str, object] = {
        "schema_version": 1,
        "state_id": UUID(STATE_ID),
        "data_root_id": UUID(DATA_ROOT_ID),
        "environment": Environment.TEST,
        "created_at": datetime(2026, 9, 20, tzinfo=UTC),
    }
    values.update(overrides)
    identity = object.__new__(RuntimeIdentity)
    for name, value in values.items():
        object.__setattr__(identity, name, value)
    return identity


@pytest.mark.parametrize("wrong_object", [None, object(), CANONICAL_BYTES])
def test_ri_l0_026_serializer_rejects_wrong_object(wrong_object: object) -> None:
    with pytest.raises(TypeError):
        serialize_runtime_identity(cast(RuntimeIdentity, wrong_object))


@pytest.mark.parametrize(
    "identity",
    [
        invalid_identity(schema_version=True),
        invalid_identity(state_id=UUID("12345678-1234-1234-9234-123456789abc")),
        invalid_identity(data_root_id=UUID("87654321-4321-1321-8321-cba987654321")),
        invalid_identity(environment="TEST"),
        invalid_identity(created_at=datetime(2026, 9, 20, tzinfo=UTC).replace(tzinfo=None)),
    ],
)
def test_ri_l0_026_serializer_rejects_invariant_violating_identity(
    identity: RuntimeIdentity,
) -> None:
    with pytest.raises(ValueError):
        serialize_runtime_identity(identity)


def test_validation_failure_requires_non_empty_errors() -> None:
    with pytest.raises(ValueError):
        RuntimeIdentityValidationFailure(errors=())


def test_ri_l0_027_repeated_calls_are_deterministic() -> None:
    first_parse = parse_runtime_identity(CANONICAL_BYTES)
    second_parse = parse_runtime_identity(CANONICAL_BYTES)
    assert isinstance(first_parse, RuntimeIdentity)
    assert isinstance(second_parse, RuntimeIdentity)
    assert first_parse == second_parse

    first_bytes = serialize_runtime_identity(first_parse)
    second_bytes = serialize_runtime_identity(first_parse)

    assert first_bytes == second_bytes == CANONICAL_BYTES


def test_ri_l0_028_parse_and_serialize_are_pure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unexpected_side_effect(*args: object, **kwargs: object) -> Any:
        raise AssertionError(f"unexpected external side effect: {args!r}, {kwargs!r}")

    monkeypatch.setattr(builtins, "open", unexpected_side_effect)
    monkeypatch.setattr(os, "open", unexpected_side_effect)
    monkeypatch.setattr(socket, "socket", unexpected_side_effect)
    module_state = dict(vars(runtime_identity_module))
    environment_state = dict(os.environ)
    valid_input = CANONICAL_BYTES
    invalid_input = b"not-json"

    valid_result = parse_runtime_identity(valid_input)
    invalid_result = parse_runtime_identity(invalid_input)
    assert isinstance(valid_result, RuntimeIdentity)
    assert_single_error(
        invalid_result,
        RuntimeIdentityValidationErrorCode.MALFORMED_JSON,
        None,
    )
    assert serialize_runtime_identity(valid_result) == CANONICAL_BYTES
    with pytest.raises(TypeError):
        serialize_runtime_identity(cast(RuntimeIdentity, object()))

    assert valid_input == CANONICAL_BYTES
    assert invalid_input == b"not-json"
    assert dict(os.environ) == environment_state
    assert vars(runtime_identity_module) == module_state
