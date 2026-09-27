from datetime import UTC, datetime
from pathlib import Path, PureWindowsPath
from typing import NoReturn
from uuid import UUID

import pytest
from argus.runtime.environment_guard import (
    ResolvedWriteTarget,
    TestEnvironmentGuardFailure,
    TestEnvironmentGuardFailureCode,
    WriteTargetPathFailure,
    WriteTargetPathFailureCode,
    resolve_test_write_target,
    verify_test_environment_startup,
)

from argus.runtime import data_root_marker_store, environment_guard
from argus.runtime.data_root_locator import DataRootLocator
from argus.runtime.data_root_marker import DataRootMarker, serialize_data_root_marker
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
CREATED_AT = datetime(2026, 9, 20, 0, 0, tzinfo=UTC)
MARKER_NAME = "data_root_marker.json"
VALID_RELATIVE_PATH = "state\\events.json"


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


def _expected(
    *,
    state_id: UUID = STATE_ID,
    data_root_id: UUID = DATA_ROOT_ID,
    environment: Environment = Environment.TEST,
) -> ExpectedEnvironmentBinding:
    return ExpectedEnvironmentBinding(state_id, data_root_id, environment)


def _locator(root: Path) -> DataRootLocator:
    return DataRootLocator(root)


def _write_marker(root: Path, marker: DataRootMarker | None = None) -> bytes:
    data = serialize_data_root_marker(marker or _marker())
    (root / MARKER_NAME).write_bytes(data)
    return data


def _snapshot(root: Path) -> dict[Path, bytes]:
    return {
        path.relative_to(root): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _assert_binding_failure(
    result: (
        VerifiedEnvironmentBinding
        | ResolvedWriteTarget
        | BindingFailure
        | TestEnvironmentGuardFailure
        | WriteTargetPathFailure
    ),
    failure_class: BindingFailureClass,
    code: BindingFailureCode,
) -> None:
    assert isinstance(result, BindingFailure)
    assert result.failure_classes == frozenset({failure_class})
    assert result.codes == (code,)


# EB-L1-020
def test_eb_l1_020_valid_test_binding_enters_startup_read_only(
    tmp_path: Path,
) -> None:
    marker_bytes = _write_marker(tmp_path)
    before = _snapshot(tmp_path)

    result = verify_test_environment_startup(_locator(tmp_path), _expected())

    assert isinstance(result, VerifiedEnvironmentBinding)
    assert result.expected == _expected()
    assert result.marker == _marker()
    assert result.locator == _locator(tmp_path)
    assert len(result.marker_content_hash) == 64
    assert _snapshot(tmp_path) == before
    assert before == {Path(MARKER_NAME): marker_bytes}


# EB-L1-021
@pytest.mark.parametrize("environment", [Environment.PAPER, Environment.LIVE])
def test_eb_l1_021_non_test_environment_is_rejected_without_io(
    tmp_path: Path,
    environment: Environment,
) -> None:
    result = verify_test_environment_startup(
        _locator(tmp_path),
        _expected(environment=environment),
    )

    assert result == TestEnvironmentGuardFailure(
        code=TestEnvironmentGuardFailureCode.TEST_ENVIRONMENT_REQUIRED,
        locator=_locator(tmp_path),
    )
    assert _snapshot(tmp_path) == {}


# EB-L1-022
@pytest.mark.parametrize("boundary", ["startup", "write"])
def test_eb_l1_022_state_mismatch_never_enters_success_state(
    tmp_path: Path,
    boundary: str,
) -> None:
    _write_marker(tmp_path, _marker(state_id=OTHER_STATE_ID))
    before = _snapshot(tmp_path)
    if boundary == "startup":
        result = verify_test_environment_startup(_locator(tmp_path), _expected())
    else:
        result = resolve_test_write_target(
            _locator(tmp_path), _expected(), VALID_RELATIVE_PATH
        )

    _assert_binding_failure(
        result,
        BindingFailureClass.ENVIRONMENT_BINDING_MISMATCH,
        BindingFailureCode.STATE_ID_MISMATCH,
    )
    assert _snapshot(tmp_path) == before


# EB-L1-023
@pytest.mark.parametrize("boundary", ["startup", "write"])
def test_eb_l1_023_data_root_mismatch_never_enters_success_state(
    tmp_path: Path,
    boundary: str,
) -> None:
    _write_marker(tmp_path, _marker(data_root_id=OTHER_DATA_ROOT_ID))
    before = _snapshot(tmp_path)
    if boundary == "startup":
        result = verify_test_environment_startup(_locator(tmp_path), _expected())
    else:
        result = resolve_test_write_target(
            _locator(tmp_path), _expected(), VALID_RELATIVE_PATH
        )

    _assert_binding_failure(
        result,
        BindingFailureClass.DATA_STORAGE_IDENTITY_MISMATCH,
        BindingFailureCode.DATA_ROOT_ID_MISMATCH,
    )
    assert _snapshot(tmp_path) == before


# EB-L1-024
@pytest.mark.parametrize("boundary", ["startup", "write"])
@pytest.mark.parametrize(
    ("marker_bytes", "code"),
    [(None, BindingFailureCode.MARKER_MISSING), (b"{", BindingFailureCode.MALFORMED_JSON)],
)
def test_eb_l1_024_missing_or_malformed_marker_is_fail_closed(
    tmp_path: Path,
    boundary: str,
    marker_bytes: bytes | None,
    code: BindingFailureCode,
) -> None:
    if marker_bytes is not None:
        (tmp_path / MARKER_NAME).write_bytes(marker_bytes)
    before = _snapshot(tmp_path)
    if boundary == "startup":
        result = verify_test_environment_startup(_locator(tmp_path), _expected())
    else:
        result = resolve_test_write_target(
            _locator(tmp_path), _expected(), VALID_RELATIVE_PATH
        )

    _assert_binding_failure(
        result,
        BindingFailureClass.DATA_STORAGE_IDENTITY_MISMATCH,
        code,
    )
    assert _snapshot(tmp_path) == before


# EB-L1-025
def test_eb_l1_025_write_boundary_performs_fresh_verification(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_marker(tmp_path)
    calls = 0
    original = environment_guard.load_and_verify_environment_binding

    def counting_load(
        locator: DataRootLocator,
        expected: ExpectedEnvironmentBinding,
    ) -> VerifiedEnvironmentBinding | BindingFailure:
        nonlocal calls
        calls += 1
        return original(locator, expected)

    monkeypatch.setattr(
        environment_guard,
        "load_and_verify_environment_binding",
        counting_load,
    )
    startup_result = verify_test_environment_startup(_locator(tmp_path), _expected())
    write_result = resolve_test_write_target(
        _locator(tmp_path), _expected(), VALID_RELATIVE_PATH
    )

    assert isinstance(startup_result, VerifiedEnvironmentBinding)
    assert isinstance(write_result, ResolvedWriteTarget)
    assert write_result.binding == startup_result
    assert calls == 2


# EB-L1-025
def test_eb_l1_025_fresh_verification_failure_blocks_write_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_marker(tmp_path)
    startup_result = verify_test_environment_startup(_locator(tmp_path), _expected())
    failure = BindingFailure(
        failure_classes=frozenset(
            {BindingFailureClass.DATA_STORAGE_IDENTITY_MISMATCH}
        ),
        codes=(BindingFailureCode.MARKER_MISSING,),
        locator=_locator(tmp_path),
    )

    def fail_fresh_verification(
        _locator_value: DataRootLocator,
        _expected_value: ExpectedEnvironmentBinding,
    ) -> VerifiedEnvironmentBinding | BindingFailure:
        return failure

    monkeypatch.setattr(
        environment_guard,
        "load_and_verify_environment_binding",
        fail_fresh_verification,
    )
    result = resolve_test_write_target(
        _locator(tmp_path), _expected(), VALID_RELATIVE_PATH
    )

    assert isinstance(startup_result, VerifiedEnvironmentBinding)
    assert result == failure
    assert not (tmp_path / "state" / "events.json").exists()


INVALID_PATH_CASES = [
    ("", WriteTargetPathFailureCode.EMPTY_PATH),
    (r"\\?\C:\root\x.json", WriteTargetPathFailureCode.DEVICE_NAMESPACE_PATH),
    (r"\\.\PIPE\argus", WriteTargetPathFailureCode.DEVICE_NAMESPACE_PATH),
    (r"//?/C:/root/x.json", WriteTargetPathFailureCode.DEVICE_NAMESPACE_PATH),
    (r"\\server\share\x.json", WriteTargetPathFailureCode.UNC_PATH),
    (r"C:\root\x.json", WriteTargetPathFailureCode.ABSOLUTE_PATH),
    (r"C:x.json", WriteTargetPathFailureCode.DRIVE_QUALIFIED_PATH),
    (r"\rooted\x.json", WriteTargetPathFailureCode.ABSOLUTE_PATH),
    (r"..\x.json", WriteTargetPathFailureCode.PARENT_TRAVERSAL),
    (r"a\..\x.json", WriteTargetPathFailureCode.PARENT_TRAVERSAL),
    (".", WriteTargetPathFailureCode.SELF_REFERENCE),
    (r"a\.\x.json", WriteTargetPathFailureCode.SELF_REFERENCE),
    (r"a\\x.json", WriteTargetPathFailureCode.EMPTY_PATH),
    ("a\\", WriteTargetPathFailureCode.EMPTY_PATH),
    ("nul\x00.json", WriteTargetPathFailureCode.INVALID_CHARACTER),
    ("a<x.json", WriteTargetPathFailureCode.INVALID_CHARACTER),
    ("a>x.json", WriteTargetPathFailureCode.INVALID_CHARACTER),
    ('a"x.json', WriteTargetPathFailureCode.INVALID_CHARACTER),
    ("a|x.json", WriteTargetPathFailureCode.INVALID_CHARACTER),
    ("a?x.json", WriteTargetPathFailureCode.INVALID_CHARACTER),
    ("a*x.json", WriteTargetPathFailureCode.INVALID_CHARACTER),
    ("x.json:stream", WriteTargetPathFailureCode.ALTERNATE_DATA_STREAM),
    ("name.\\x.json", WriteTargetPathFailureCode.TRAILING_DOT_OR_SPACE),
    ("name \\x.json", WriteTargetPathFailureCode.TRAILING_DOT_OR_SPACE),
]


# EB-L1-026
@pytest.mark.parametrize(("relative_path", "code"), INVALID_PATH_CASES)
def test_eb_l1_026_rejects_closed_invalid_path_classes_before_io(
    tmp_path: Path,
    relative_path: str,
    code: WriteTargetPathFailureCode,
) -> None:
    result = resolve_test_write_target(_locator(tmp_path), _expected(), relative_path)

    assert result == WriteTargetPathFailure(code=code, relative_path=relative_path)
    assert _snapshot(tmp_path) == {}


RESERVED_NAMES = [
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
]


# EB-L1-026
@pytest.mark.parametrize("reserved_name", RESERVED_NAMES)
def test_eb_l1_026_rejects_all_reserved_device_basenames_case_insensitively(
    tmp_path: Path,
    reserved_name: str,
) -> None:
    relative_path = f"safe\\{reserved_name.lower()}.json"
    result = resolve_test_write_target(_locator(tmp_path), _expected(), relative_path)

    assert result == WriteTargetPathFailure(
        code=WriteTargetPathFailureCode.RESERVED_DEVICE_NAME,
        relative_path=relative_path,
    )
    assert _snapshot(tmp_path) == {}


# EB-L1-026
def test_eb_l1_026_resolves_mixed_separators_inside_verified_root(
    tmp_path: Path,
) -> None:
    _write_marker(tmp_path)
    result = resolve_test_write_target(
        _locator(tmp_path),
        _expected(),
        "state/events\\2026.json",
    )

    assert isinstance(result, ResolvedWriteTarget)
    assert result.relative_path == PureWindowsPath(r"state\events\2026.json")
    assert result.target_path == tmp_path / "state" / "events" / "2026.json"
    assert result.binding.locator == _locator(tmp_path)


# EB-L1-026
def test_eb_l1_026_rejects_non_absolute_verified_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    locator = _locator(Path("relative-root"))
    binding = VerifiedEnvironmentBinding(
        expected=_expected(),
        marker=_marker(),
        locator=locator,
        marker_content_hash="0" * 64,
    )

    def return_relative_binding(
        _locator_value: DataRootLocator,
        _expected_value: ExpectedEnvironmentBinding,
    ) -> VerifiedEnvironmentBinding | BindingFailure:
        return binding

    monkeypatch.setattr(
        environment_guard,
        "load_and_verify_environment_binding",
        return_relative_binding,
    )
    result = resolve_test_write_target(locator, _expected(), VALID_RELATIVE_PATH)

    assert result == WriteTargetPathFailure(
        code=WriteTargetPathFailureCode.INVALID_VERIFIED_ROOT,
        relative_path=VALID_RELATIVE_PATH,
    )


# EB-L1-027
@pytest.mark.parametrize(
    "case",
    [
        "startup_success",
        "write_success",
        "startup_binding_failure",
        "write_binding_failure",
        "startup_guard_failure",
        "write_guard_failure",
        "write_path_failure",
    ],
)
def test_eb_l1_027_all_guard_outcomes_never_initialize_or_modify_marker(
    tmp_path: Path,
    case: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_if_initialized(
        _locator_value: DataRootLocator,
        _marker_value: DataRootMarker,
    ) -> NoReturn:
        raise AssertionError("guard called the explicit marker initialization API")

    monkeypatch.setattr(
        data_root_marker_store,
        "initialize_data_root_marker",
        fail_if_initialized,
    )
    expected = _expected()
    relative_path = VALID_RELATIVE_PATH
    if "success" in case:
        _write_marker(tmp_path)
    elif "binding_failure" in case:
        (tmp_path / MARKER_NAME).write_bytes(b"{")
    elif "guard_failure" in case:
        expected = _expected(environment=Environment.PAPER)
    else:
        relative_path = r"..\outside.json"
    before = _snapshot(tmp_path)

    if case.startswith("startup"):
        result = verify_test_environment_startup(_locator(tmp_path), expected)
    else:
        result = resolve_test_write_target(
            _locator(tmp_path), expected, relative_path
        )

    if "success" in case:
        if case.startswith("startup"):
            assert isinstance(result, VerifiedEnvironmentBinding)
        else:
            assert isinstance(result, ResolvedWriteTarget)
    elif "binding_failure" in case:
        _assert_binding_failure(
            result,
            BindingFailureClass.DATA_STORAGE_IDENTITY_MISMATCH,
            BindingFailureCode.MALFORMED_JSON,
        )
    elif "guard_failure" in case:
        assert result == TestEnvironmentGuardFailure(
            code=TestEnvironmentGuardFailureCode.TEST_ENVIRONMENT_REQUIRED,
            locator=_locator(tmp_path),
        )
    else:
        assert result == WriteTargetPathFailure(
            code=WriteTargetPathFailureCode.PARENT_TRAVERSAL,
            relative_path=relative_path,
        )
    assert _snapshot(tmp_path) == before
