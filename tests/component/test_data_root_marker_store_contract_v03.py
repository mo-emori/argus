from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from uuid import UUID

import pytest

from argus.runtime import data_root_marker_store as marker_store
from argus.runtime.data_root_locator import DataRootLocator
from argus.runtime.data_root_marker import DataRootMarker, serialize_data_root_marker
from argus.runtime.data_root_marker_store import (
    DataRootInitializationUnavailable,
    LoadedDataRootMarker,
    MarkerAlreadyExists,
    MarkerAtomicWriteFailed,
    MarkerReloadVerificationFailed,
    initialize_data_root_marker,
    load_and_verify_environment_binding,
    load_data_root_marker,
)
from argus.runtime.environment import Environment
from argus.runtime.environment_binding import (
    BindingFailure,
    BindingFailureClass,
    BindingFailureCode,
    ExpectedEnvironmentBinding,
    VerifiedEnvironmentBinding,
)

STATE_ID = UUID("12345678-1234-4234-9234-123456789abc")
OTHER_STATE_ID = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
DATA_ROOT_ID = UUID("87654321-4321-4321-8321-cba987654321")
OTHER_DATA_ROOT_ID = UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")
CREATED_AT = datetime(2026, 9, 18, 12, 34, 56, 123456, tzinfo=UTC)
MARKER_NAME = "data_root_marker.json"


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


def _expected() -> ExpectedEnvironmentBinding:
    return ExpectedEnvironmentBinding(STATE_ID, DATA_ROOT_ID, Environment.TEST)


def _locator(path: Path) -> DataRootLocator:
    return DataRootLocator(path)


def _write_marker(root: Path, marker: DataRootMarker | None = None) -> bytes:
    data = serialize_data_root_marker(marker or _marker())
    (root / MARKER_NAME).write_bytes(data)
    return data


def _assert_failure(
    result: LoadedDataRootMarker | VerifiedEnvironmentBinding | BindingFailure,
    locator: DataRootLocator,
    failure_classes: frozenset[BindingFailureClass],
    codes: tuple[BindingFailureCode, ...],
) -> None:
    assert isinstance(result, BindingFailure)
    assert result.locator == locator
    assert result.failure_classes == failure_classes
    assert result.codes == codes


# EB-L1-001
def test_eb_l1_001_loads_fixed_marker_once_and_hashes_the_read_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    marker_bytes = _write_marker(tmp_path)
    reads = 0
    original_read = Path.read_bytes

    def counting_read(path: Path) -> bytes:
        nonlocal reads
        reads += 1
        return original_read(path)

    monkeypatch.setattr(Path, "read_bytes", counting_read)
    result = load_data_root_marker(_locator(tmp_path))

    assert isinstance(result, LoadedDataRootMarker)
    assert result.marker == _marker()
    assert result.marker_content_hash == sha256(marker_bytes).hexdigest()
    assert reads == 1


# EB-L1-002
def test_eb_l1_002_missing_data_root_is_unavailable(tmp_path: Path) -> None:
    locator = _locator(tmp_path / "missing")
    result = load_data_root_marker(locator)
    _assert_failure(
        result,
        locator,
        frozenset({BindingFailureClass.DATA_STORAGE_UNAVAILABLE}),
        (BindingFailureCode.DATA_ROOT_MISSING,),
    )
    assert not locator.path.exists()


# EB-L1-003
def test_eb_l1_003_missing_marker_is_identity_mismatch(tmp_path: Path) -> None:
    locator = _locator(tmp_path)
    result = load_data_root_marker(locator)
    _assert_failure(
        result,
        locator,
        frozenset({BindingFailureClass.DATA_STORAGE_IDENTITY_MISMATCH}),
        (BindingFailureCode.MARKER_MISSING,),
    )
    assert not (tmp_path / MARKER_NAME).exists()


@pytest.mark.parametrize("winerror", [5, 65])
def test_eb_l1_004_access_denied_winerrors_are_classified(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    winerror: int,
) -> None:
    locator = _locator(tmp_path)
    def fail_read(_path: Path) -> bytes:
        return _raise_os_error(winerror)

    monkeypatch.setattr(Path, "read_bytes", fail_read)
    result = load_data_root_marker(locator)
    _assert_failure(
        result,
        locator,
        frozenset({BindingFailureClass.DATA_STORAGE_UNAVAILABLE}),
        (BindingFailureCode.DATA_ROOT_ACCESS_DENIED,),
    )


@pytest.mark.parametrize("winerror", [15, 20, 21, 53, 55, 67, 321])
def test_eb_l1_005_device_unavailable_closed_winerror_set(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    winerror: int,
) -> None:
    locator = _locator(tmp_path)
    def fail_read(_path: Path) -> bytes:
        return _raise_os_error(winerror)

    monkeypatch.setattr(Path, "read_bytes", fail_read)
    result = load_data_root_marker(locator)
    _assert_failure(
        result,
        locator,
        frozenset({BindingFailureClass.DATA_STORAGE_UNAVAILABLE}),
        (BindingFailureCode.DEVICE_UNAVAILABLE,),
    )


def _raise_os_error(winerror: int) -> bytes:
    error = OSError(winerror, "injected filesystem failure")
    error.winerror = winerror
    raise error


# EB-L1-006
def test_eb_l1_006_unclassified_read_error_is_marker_read_failed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    locator = _locator(tmp_path)
    def fail_read(_path: Path) -> bytes:
        return _raise_os_error(999)

    monkeypatch.setattr(Path, "read_bytes", fail_read)
    result = load_data_root_marker(locator)
    _assert_failure(
        result,
        locator,
        frozenset({BindingFailureClass.DATA_STORAGE_UNAVAILABLE}),
        (BindingFailureCode.MARKER_READ_FAILED,),
    )


def test_eb_l1_006_existing_non_directory_root_is_marker_read_failed(
    tmp_path: Path,
) -> None:
    root_file = tmp_path / "not-a-directory"
    root_file.write_bytes(b"")
    locator = _locator(root_file)
    result = load_data_root_marker(locator)
    _assert_failure(
        result,
        locator,
        frozenset({BindingFailureClass.DATA_STORAGE_UNAVAILABLE}),
        (BindingFailureCode.MARKER_READ_FAILED,),
    )


# EB-L1-007
def test_eb_l1_007_malformed_json_is_identity_mismatch(tmp_path: Path) -> None:
    (tmp_path / MARKER_NAME).write_bytes(b"{")
    locator = _locator(tmp_path)
    result = load_data_root_marker(locator)
    _assert_failure(
        result,
        locator,
        frozenset({BindingFailureClass.DATA_STORAGE_IDENTITY_MISMATCH}),
        (BindingFailureCode.MALFORMED_JSON,),
    )


# EB-L1-008
def test_eb_l1_008_all_validation_codes_and_order_are_preserved(tmp_path: Path) -> None:
    (tmp_path / MARKER_NAME).write_text(
        '{"schema_version":2,"state_id":"bad","data_root_id":"bad",'
        '"environment":"bad","created_at":"bad"}\n',
        encoding="utf-8",
        newline="\n",
    )
    locator = _locator(tmp_path)
    result = load_data_root_marker(locator)
    _assert_failure(
        result,
        locator,
        frozenset({BindingFailureClass.DATA_STORAGE_IDENTITY_MISMATCH}),
        (
            BindingFailureCode.UNSUPPORTED_SCHEMA_VERSION,
            BindingFailureCode.INVALID_STATE_ID,
            BindingFailureCode.INVALID_DATA_ROOT_ID,
            BindingFailureCode.INVALID_ENVIRONMENT,
            BindingFailureCode.INVALID_CREATED_AT,
        ),
    )


# EB-L1-009
def test_eb_l1_009_explicit_initialization_publishes_and_reloads_marker(
    tmp_path: Path,
) -> None:
    result = initialize_data_root_marker(_locator(tmp_path), _marker())
    assert isinstance(result, DataRootMarker)
    assert result == _marker()
    assert (tmp_path / MARKER_NAME).is_file()


# EB-L1-010
def test_eb_l1_010_existing_marker_is_never_overwritten(tmp_path: Path) -> None:
    existing = _write_marker(tmp_path)
    result = initialize_data_root_marker(_locator(tmp_path), _marker())
    assert isinstance(result, MarkerAlreadyExists)
    assert (tmp_path / MARKER_NAME).read_bytes() == existing


# EB-L1-011
def test_eb_l1_011_pre_publish_failure_never_creates_final_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_publish(_temp_path: Path, _target_path: Path) -> None:
        raise OSError(999, "injected publish failure")

    monkeypatch.setattr(marker_store, "_publish_no_replace", fail_publish)
    result = initialize_data_root_marker(_locator(tmp_path), _marker())
    assert isinstance(result, MarkerAtomicWriteFailed)
    assert not (tmp_path / MARKER_NAME).exists()


def test_eb_l1_011_publish_race_returns_already_exists_without_overwrite(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    competing_bytes = b"competing initializer"

    def competing_publish(_temp_path: Path, target_path: Path) -> None:
        target_path.write_bytes(competing_bytes)
        raise FileExistsError(target_path)

    monkeypatch.setattr(marker_store, "_publish_no_replace", competing_publish)
    result = initialize_data_root_marker(_locator(tmp_path), _marker())
    assert isinstance(result, MarkerAlreadyExists)
    assert (tmp_path / MARKER_NAME).read_bytes() == competing_bytes


# EB-L1-012
def test_eb_l1_012_post_publish_reload_failure_keeps_final_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_reload(locator: DataRootLocator) -> LoadedDataRootMarker | BindingFailure:
        return BindingFailure(
            frozenset({BindingFailureClass.DATA_STORAGE_UNAVAILABLE}),
            (BindingFailureCode.MARKER_READ_FAILED,),
            locator,
        )

    monkeypatch.setattr(marker_store, "load_data_root_marker", fail_reload)
    result = initialize_data_root_marker(_locator(tmp_path), _marker())
    assert isinstance(result, MarkerReloadVerificationFailed)
    assert (tmp_path / MARKER_NAME).exists()


@pytest.mark.parametrize(
    ("test_id", "marker", "classes", "codes"),
    [
        pytest.param(
            "EB-L1-014",
            _marker(state_id=OTHER_STATE_ID),
            frozenset({BindingFailureClass.ENVIRONMENT_BINDING_MISMATCH}),
            (BindingFailureCode.STATE_ID_MISMATCH,),
            id="EB-L1-014-state",
        ),
        pytest.param(
            "EB-L1-015",
            _marker(data_root_id=OTHER_DATA_ROOT_ID),
            frozenset({BindingFailureClass.DATA_STORAGE_IDENTITY_MISMATCH}),
            (BindingFailureCode.DATA_ROOT_ID_MISMATCH,),
            id="EB-L1-015-data-root",
        ),
        pytest.param(
            "EB-L1-016",
            _marker(environment=Environment.PAPER),
            frozenset({BindingFailureClass.ENVIRONMENT_BINDING_MISMATCH}),
            (BindingFailureCode.ENVIRONMENT_MISMATCH,),
            id="EB-L1-016-environment",
        ),
        pytest.param(
            "EB-L1-017",
            _marker(
                state_id=OTHER_STATE_ID,
                data_root_id=OTHER_DATA_ROOT_ID,
                environment=Environment.PAPER,
            ),
            frozenset(
                {
                    BindingFailureClass.ENVIRONMENT_BINDING_MISMATCH,
                    BindingFailureClass.DATA_STORAGE_IDENTITY_MISMATCH,
                }
            ),
            (
                BindingFailureCode.STATE_ID_MISMATCH,
                BindingFailureCode.DATA_ROOT_ID_MISMATCH,
                BindingFailureCode.ENVIRONMENT_MISMATCH,
            ),
            id="EB-L1-017-all",
        ),
    ],
)
def test_eb_l1_014_through_017_load_and_verify_mismatches(
    tmp_path: Path,
    test_id: str,
    marker: DataRootMarker,
    classes: frozenset[BindingFailureClass],
    codes: tuple[BindingFailureCode, ...],
) -> None:
    del test_id
    _write_marker(tmp_path, marker)
    locator = _locator(tmp_path)
    result = load_and_verify_environment_binding(locator, _expected())
    _assert_failure(result, locator, classes, codes)


# EB-L1-013, EB-L1-018
def test_eb_l1_013_and_018_load_and_verify_success_uses_actual_read_hash(
    tmp_path: Path,
) -> None:
    marker_bytes = _write_marker(tmp_path)
    locator = _locator(tmp_path)
    result = load_and_verify_environment_binding(locator, _expected())
    assert isinstance(result, VerifiedEnvironmentBinding)
    assert result.locator == locator
    assert result.marker == _marker()
    assert result.expected == _expected()
    assert result.marker_content_hash == sha256(marker_bytes).hexdigest()


def test_eb_l1_009_unavailable_root_returns_explicit_value(tmp_path: Path) -> None:
    locator = _locator(tmp_path / "missing")
    result = initialize_data_root_marker(locator, _marker())
    assert isinstance(result, DataRootInitializationUnavailable)
    assert not locator.path.exists()


# FINDING-02 / EB-L1-012 coverage extension
def test_finding_02_valid_but_different_reload_keeps_published_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    intended_marker = _marker()
    reloaded_marker = _marker(data_root_id=OTHER_DATA_ROOT_ID)

    def reload_different(
        _locator: DataRootLocator,
    ) -> LoadedDataRootMarker | BindingFailure:
        reloaded_bytes = serialize_data_root_marker(reloaded_marker)
        return LoadedDataRootMarker(
            marker=reloaded_marker,
            marker_content_hash=sha256(reloaded_bytes).hexdigest(),
        )

    monkeypatch.setattr(marker_store, "load_data_root_marker", reload_different)
    result = initialize_data_root_marker(_locator(tmp_path), intended_marker)
    target = tmp_path / MARKER_NAME

    assert isinstance(result, MarkerReloadVerificationFailed)
    assert target.is_file()
    assert target.read_bytes() == serialize_data_root_marker(intended_marker)

