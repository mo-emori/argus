from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest
from argus.runtime.data_root_locator import DataRootLocator
from argus.runtime.environment_binding import (
    BindingFailure,
    BindingFailureClass,
    BindingFailureCode,
    ExpectedEnvironmentBinding,
    VerifiedEnvironmentBinding,
    verify_environment_binding,
)

from argus.runtime.data_root_marker import DataRootMarker
from argus.runtime.environment import Environment

STATE_ID = UUID("12345678-1234-4234-9234-123456789abc")
OTHER_STATE_ID = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
DATA_ROOT_ID = UUID("87654321-4321-4321-8321-cba987654321")
OTHER_DATA_ROOT_ID = UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")
CREATED_AT = datetime(2026, 9, 16, 0, 0, tzinfo=UTC)
VALID_MARKER_CONTENT_HASH = "a" * 64
OTHER_VALID_MARKER_CONTENT_HASH = "b" * 64


def _expected_binding() -> ExpectedEnvironmentBinding:
    return ExpectedEnvironmentBinding(
        state_id=STATE_ID,
        data_root_id=DATA_ROOT_ID,
        environment=Environment.TEST,
    )


def _marker(
    *,
    state_id: UUID = STATE_ID,
    data_root_id: UUID = DATA_ROOT_ID,
    environment: Environment = Environment.TEST,
) -> DataRootMarker:
    return DataRootMarker(
        schema_version=1,
        state_id=state_id,
        data_root_id=data_root_id,
        environment=environment,
        created_at=CREATED_AT,
    )


def _locator() -> DataRootLocator:
    return DataRootLocator(path=Path("L:/emori/InvestmentAgentTestData"))


def test_eb_l0_020_all_identities_match() -> None:
    expected = _expected_binding()
    marker = _marker()
    locator = _locator()

    result = verify_environment_binding(
        locator,
        marker,
        VALID_MARKER_CONTENT_HASH,
        expected,
    )

    assert not isinstance(result, BindingFailure)
    assert isinstance(result, VerifiedEnvironmentBinding)
    assert result.expected == expected
    assert result.marker == marker
    assert result.locator == locator
    assert result.marker_content_hash == VALID_MARKER_CONTENT_HASH


def test_eb_l0_021_state_id_mismatch() -> None:
    locator = _locator()

    result = verify_environment_binding(
        locator,
        _marker(state_id=OTHER_STATE_ID),
        VALID_MARKER_CONTENT_HASH,
        _expected_binding(),
    )

    assert isinstance(result, BindingFailure)
    assert result.failure_classes == frozenset(
        {BindingFailureClass.ENVIRONMENT_BINDING_MISMATCH}
    )
    assert result.codes == (BindingFailureCode.STATE_ID_MISMATCH,)
    assert result.locator == locator
    assert BindingFailureCode.DATA_ROOT_ID_MISMATCH not in result.codes
    assert BindingFailureCode.ENVIRONMENT_MISMATCH not in result.codes
    assert (
        BindingFailureClass.DATA_STORAGE_IDENTITY_MISMATCH
        not in result.failure_classes
    )


def test_eb_l0_022_data_root_id_mismatch() -> None:
    locator = _locator()

    result = verify_environment_binding(
        locator,
        _marker(data_root_id=OTHER_DATA_ROOT_ID),
        VALID_MARKER_CONTENT_HASH,
        _expected_binding(),
    )

    assert isinstance(result, BindingFailure)
    assert result.failure_classes == frozenset(
        {BindingFailureClass.DATA_STORAGE_IDENTITY_MISMATCH}
    )
    assert result.codes == (BindingFailureCode.DATA_ROOT_ID_MISMATCH,)
    assert result.locator == locator
    assert BindingFailureCode.STATE_ID_MISMATCH not in result.codes
    assert BindingFailureCode.ENVIRONMENT_MISMATCH not in result.codes
    assert BindingFailureClass.ENVIRONMENT_BINDING_MISMATCH not in result.failure_classes


def test_eb_l0_023_environment_mismatch() -> None:
    locator = _locator()

    result = verify_environment_binding(
        locator,
        _marker(environment=Environment.PAPER),
        VALID_MARKER_CONTENT_HASH,
        _expected_binding(),
    )

    assert isinstance(result, BindingFailure)
    assert result.failure_classes == frozenset(
        {BindingFailureClass.ENVIRONMENT_BINDING_MISMATCH}
    )
    assert result.codes == (BindingFailureCode.ENVIRONMENT_MISMATCH,)
    assert result.locator == locator
    assert BindingFailureCode.STATE_ID_MISMATCH not in result.codes
    assert BindingFailureCode.DATA_ROOT_ID_MISMATCH not in result.codes
    assert (
        BindingFailureClass.DATA_STORAGE_IDENTITY_MISMATCH
        not in result.failure_classes
    )


@pytest.mark.parametrize(
    ("state_mismatch", "data_root_mismatch", "environment_mismatch"),
    [
        pytest.param(True, True, False, id="state-and-data-root"),
        pytest.param(True, False, True, id="state-and-environment"),
        pytest.param(False, True, True, id="data-root-and-environment"),
        pytest.param(True, True, True, id="all-three"),
    ],
)
def test_eb_l0_024_multiple_mismatches_are_preserved_in_normative_order(
    state_mismatch: bool,
    data_root_mismatch: bool,
    environment_mismatch: bool,
) -> None:
    locator = _locator()
    result = verify_environment_binding(
        locator,
        _marker(
            state_id=OTHER_STATE_ID if state_mismatch else STATE_ID,
            data_root_id=(
                OTHER_DATA_ROOT_ID if data_root_mismatch else DATA_ROOT_ID
            ),
            environment=Environment.PAPER if environment_mismatch else Environment.TEST,
        ),
        VALID_MARKER_CONTENT_HASH,
        _expected_binding(),
    )
    expected_classes = frozenset(
        failure_class
        for condition, failure_class in (
            (state_mismatch, BindingFailureClass.ENVIRONMENT_BINDING_MISMATCH),
            (
                data_root_mismatch,
                BindingFailureClass.DATA_STORAGE_IDENTITY_MISMATCH,
            ),
            (
                environment_mismatch,
                BindingFailureClass.ENVIRONMENT_BINDING_MISMATCH,
            ),
        )
        if condition
    )
    expected_codes = tuple(
        code
        for condition, code in (
            (state_mismatch, BindingFailureCode.STATE_ID_MISMATCH),
            (data_root_mismatch, BindingFailureCode.DATA_ROOT_ID_MISMATCH),
            (environment_mismatch, BindingFailureCode.ENVIRONMENT_MISMATCH),
        )
        if condition
    )

    assert isinstance(result, BindingFailure)
    assert result.failure_classes == expected_classes
    assert result.codes == expected_codes
    assert result.locator == locator


def test_eb_l0_025_verified_binding_retains_locator() -> None:
    locator = _locator()

    result = verify_environment_binding(
        locator,
        _marker(),
        VALID_MARKER_CONTENT_HASH,
        _expected_binding(),
    )

    assert isinstance(result, VerifiedEnvironmentBinding)
    assert result.locator == locator


def test_eb_l0_026_verified_binding_retains_marker_content_hash() -> None:
    result = verify_environment_binding(
        _locator(),
        _marker(),
        VALID_MARKER_CONTENT_HASH,
        _expected_binding(),
    )

    assert isinstance(result, VerifiedEnvironmentBinding)
    assert result.marker_content_hash == VALID_MARKER_CONTENT_HASH


def test_eb_l0_026_hash_does_not_participate_in_identity_comparison() -> None:
    locator = _locator()
    marker = _marker()
    expected = _expected_binding()

    first_result = verify_environment_binding(
        locator,
        marker,
        VALID_MARKER_CONTENT_HASH,
        expected,
    )
    second_result = verify_environment_binding(
        locator,
        marker,
        OTHER_VALID_MARKER_CONTENT_HASH,
        expected,
    )

    assert isinstance(first_result, VerifiedEnvironmentBinding)
    assert isinstance(second_result, VerifiedEnvironmentBinding)
    assert first_result.marker_content_hash == VALID_MARKER_CONTENT_HASH
    assert second_result.marker_content_hash == OTHER_VALID_MARKER_CONTENT_HASH
