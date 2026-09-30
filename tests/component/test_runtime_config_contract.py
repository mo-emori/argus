import builtins
import json
import os
import random
import socket
import time
from pathlib import Path

import pytest

from argus.runtime.runtime_config import (
    RuntimeConfigDiagnostic,
    RuntimeConfigDiagnosticCode,
    RuntimeConfigResult,
    RuntimeConfigSnapshot,
    RuntimeConfigState,
    ValidatedRuntimeConfig,
    load_runtime_config,
    parse_runtime_config,
)

VALID_BYTES = b'{"config_version":1,"data_root":"data"}'
RESOLUTION_FAILURE_MARKER = "__ARGUS_TEST_DATA_ROOT_RESOLUTION_FAILURE__"


def config_bytes(*, config_version: object = 1, data_root: object = "data") -> bytes:
    return json.dumps(
        {"config_version": config_version, "data_root": data_root},
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode()


def diagnostic(
    code: RuntimeConfigDiagnosticCode,
    field_name: str | None,
) -> RuntimeConfigDiagnostic:
    return RuntimeConfigDiagnostic(code=code, field_name=field_name)


def assert_failure(
    result: RuntimeConfigResult,
    state: RuntimeConfigState,
    *diagnostics: RuntimeConfigDiagnostic,
) -> None:
    assert result.state is state
    assert result.snapshot is None
    assert result.diagnostics == diagnostics


def assert_l0_success(
    result: RuntimeConfigResult,
    data_root: str = "data",
) -> ValidatedRuntimeConfig:
    assert result.state is RuntimeConfigState.CONFIGURED
    assert result.snapshot == ValidatedRuntimeConfig(config_version=1, data_root=data_root)
    assert result.diagnostics == ()
    assert isinstance(result.snapshot, ValidatedRuntimeConfig)
    return result.snapshot


def write_config(config_path: Path, data: bytes = VALID_BYTES) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_bytes(data)


def lexical(path: Path) -> Path:
    return Path(os.path.normpath(os.path.abspath(path)))


def assert_l1_success(
    result: RuntimeConfigResult,
    *,
    data_root: str,
    config_path: Path,
) -> RuntimeConfigSnapshot:
    expected_config_path = lexical(config_path)
    expected_data_root_path = Path(os.path.normpath(expected_config_path.parent / data_root))
    assert result.state is RuntimeConfigState.CONFIGURED
    assert result.snapshot == RuntimeConfigSnapshot(
        config_version=1,
        data_root=data_root,
        config_path=expected_config_path,
        data_root_path=expected_data_root_path,
    )
    assert result.diagnostics == ()
    assert isinstance(result.snapshot, RuntimeConfigSnapshot)
    return result.snapshot


# RC-L0-001
def test_rc_l0_001_minimal_document_is_configured() -> None:
    assert_l0_success(parse_runtime_config(VALID_BYTES))


# RC-L0-002
def test_rc_l0_002_exact_integer_version_one_is_accepted() -> None:
    snapshot = assert_l0_success(parse_runtime_config(config_bytes(config_version=1)))
    assert snapshot.config_version == 1
    assert type(snapshot.config_version) is int


# RC-L0-003
@pytest.mark.parametrize("version", [0, 2, -1])
def test_rc_l0_003_unsupported_integer_versions_are_invalid(version: int) -> None:
    assert_failure(
        parse_runtime_config(config_bytes(config_version=version)),
        RuntimeConfigState.INVALID,
        diagnostic(RuntimeConfigDiagnosticCode.UNSUPPORTED_CONFIG_VERSION, "config_version"),
    )


# RC-L0-004
@pytest.mark.parametrize(
    ("data", "missing_fields"),
    [
        pytest.param(b"{}", ("config_version", "data_root"), id="both-canonical-order"),
        pytest.param(b'{"data_root":"data"}', ("config_version",), id="version"),
        pytest.param(b'{"config_version":1}', ("data_root",), id="data-root"),
        pytest.param(
            b'{"future":false}',
            ("config_version", "data_root"),
            id="missing-precedes-unknown-and-later-phases",
        ),
    ],
)
def test_rc_l0_004_missing_fields_are_reported_in_canonical_order(
    data: bytes,
    missing_fields: tuple[str, ...],
) -> None:
    expected = tuple(
        diagnostic(RuntimeConfigDiagnosticCode.MISSING_FIELD, field) for field in missing_fields
    )
    if data == b'{"future":false}':
        expected += (diagnostic(RuntimeConfigDiagnosticCode.UNKNOWN_KEY, "future"),)
    assert_failure(parse_runtime_config(data), RuntimeConfigState.INVALID, *expected)


# RC-L0-005
def test_rc_l0_005_unknown_keys_are_preserved_in_encounter_order() -> None:
    data = b'{"future_b":2,"config_version":1,"future_a":1,"data_root":"data"}'
    assert_failure(
        parse_runtime_config(data),
        RuntimeConfigState.INVALID,
        diagnostic(RuntimeConfigDiagnosticCode.UNKNOWN_KEY, "future_b"),
        diagnostic(RuntimeConfigDiagnosticCode.UNKNOWN_KEY, "future_a"),
    )


# RC-L0-006
@pytest.mark.parametrize(
    ("data", "duplicate"),
    [
        pytest.param(
            b'{"config_version":1,"data_root":"first","data\\u005froot":"second"}',
            "data_root",
            id="escaped-key-collides-after-decoding",
        ),
        pytest.param(
            b'{"config_version":1,"config_version":2,"data_root":"x","data_root":"y"}',
            "config_version",
            id="first-duplicate-only",
        ),
    ],
)
def test_rc_l0_006_duplicate_keys_are_detected_from_raw_json(
    data: bytes,
    duplicate: str,
) -> None:
    assert_failure(
        parse_runtime_config(data),
        RuntimeConfigState.INVALID,
        diagnostic(RuntimeConfigDiagnosticCode.DUPLICATE_KEY, duplicate),
    )


# RC-L0-007
@pytest.mark.parametrize(
    "data",
    [
        pytest.param(b"\xff", id="invalid-utf8"),
        pytest.param(b"\xef\xbb\xbf" + VALID_BYTES, id="utf8-bom"),
        pytest.param(b'{"config_version":1', id="truncated"),
        pytest.param(VALID_BYTES + b" false", id="trailing-data"),
        pytest.param(b'{"config_version":NaN,"data_root":"data"}', id="nan"),
        pytest.param(b'{"config_version":Infinity,"data_root":"data"}', id="infinity"),
        pytest.param(b'{"config_version":-Infinity,"data_root":"data"}', id="negative-infinity"),
    ],
)
def test_rc_l0_007_non_strict_json_is_malformed(data: bytes) -> None:
    assert_failure(
        parse_runtime_config(data),
        RuntimeConfigState.INVALID,
        diagnostic(RuntimeConfigDiagnosticCode.MALFORMED_JSON, None),
    )


def test_rc_l0_007_rfc_8259_surrounding_whitespace_is_accepted() -> None:
    assert_l0_success(parse_runtime_config(b" \t\r\n" + VALID_BYTES + b"\n\r\t "))


# RC-L0-008
@pytest.mark.parametrize("value", ["1", 1.0, None, [], {}, True, False])
def test_rc_l0_008_config_version_types_are_not_coerced(value: object) -> None:
    assert_failure(
        parse_runtime_config(config_bytes(config_version=value)),
        RuntimeConfigState.INVALID,
        diagnostic(RuntimeConfigDiagnosticCode.INVALID_FIELD_TYPE, "config_version"),
    )


# RC-L0-009
@pytest.mark.parametrize("value", [1, 1.0, None, [], {}, True])
def test_rc_l0_009_data_root_must_be_a_string(value: object) -> None:
    assert_failure(
        parse_runtime_config(config_bytes(data_root=value)),
        RuntimeConfigState.INVALID,
        diagnostic(RuntimeConfigDiagnosticCode.INVALID_FIELD_TYPE, "data_root"),
    )


def test_rc_l0_009_multiple_type_errors_use_canonical_order_and_stop_value_phase() -> None:
    assert_failure(
        parse_runtime_config(config_bytes(config_version="bad", data_root=0)),
        RuntimeConfigState.INVALID,
        diagnostic(RuntimeConfigDiagnosticCode.INVALID_FIELD_TYPE, "config_version"),
        diagnostic(RuntimeConfigDiagnosticCode.INVALID_FIELD_TYPE, "data_root"),
    )


# RC-L0-010
@pytest.mark.parametrize(
    "value",
    [
        ".",
        "..",
        "../outside",
        "a/./b",
        r"a\..\b",
        "mixed\\and/separators",
        " CON ",
        "name. ",
        "$ARGUS_HOME/data",
        "~/data",
        ":relative",
        "é:data",
    ],
)
def test_rc_l0_010_contract_relative_strings_are_preserved_exactly(value: str) -> None:
    snapshot = assert_l0_success(parse_runtime_config(config_bytes(data_root=value)), value)
    assert snapshot.data_root == value


# RC-L0-011
@pytest.mark.parametrize(
    "value",
    [
        "",
        "nul\x00path",
        "/rooted",
        r"\rooted",
        r"\\server\share",
        r"\\?\C:\device",
        "C:/absolute",
        r"C:\absolute",
        "C:relative",
        "z:relative",
    ],
)
def test_rc_l0_011_absolute_like_or_nul_data_root_is_invalid(value: str) -> None:
    assert_failure(
        parse_runtime_config(config_bytes(data_root=value)),
        RuntimeConfigState.INVALID,
        diagnostic(RuntimeConfigDiagnosticCode.INVALID_DATA_ROOT, "data_root"),
    )


# RC-L0-012
@pytest.mark.parametrize("data", [b"null", b"[]", b'"value"', b"1", b"true"])
def test_rc_l0_012_non_object_root_is_terminal(data: bytes) -> None:
    assert_failure(
        parse_runtime_config(data),
        RuntimeConfigState.INVALID,
        diagnostic(RuntimeConfigDiagnosticCode.JSON_ROOT_NOT_OBJECT, None),
    )


# RC-L0-013
@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            b'{"config_version":1,"config_version":2,"unknown":0}',
            ((RuntimeConfigDiagnosticCode.DUPLICATE_KEY, "config_version"),),
            id="duplicate-precedes-structure-type-value",
        ),
        pytest.param(
            b'{"unknown":0,"config_version":"bad"}',
            (
                (RuntimeConfigDiagnosticCode.MISSING_FIELD, "data_root"),
                (RuntimeConfigDiagnosticCode.UNKNOWN_KEY, "unknown"),
            ),
            id="missing-precedes-unknown-type-value",
        ),
        pytest.param(
            b'{"config_version":"bad","data_root":""}',
            ((RuntimeConfigDiagnosticCode.INVALID_FIELD_TYPE, "config_version"),),
            id="type-precedes-value",
        ),
    ],
)
def test_rc_l0_013_validation_phase_precedence_is_deterministic(
    data: bytes,
    expected: tuple[tuple[RuntimeConfigDiagnosticCode, str | None], ...],
) -> None:
    result = parse_runtime_config(data)
    assert result.state is RuntimeConfigState.INVALID
    assert result.snapshot is None
    assert result.diagnostics == tuple(diagnostic(*item) for item in expected)


# RC-L0-014
@pytest.mark.parametrize("data", [VALID_BYTES, b"{"])
def test_rc_l0_014_parser_is_pure_and_does_not_access_filesystem(
    data: bytes,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = bytes(data)

    def forbidden(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("L0 accessed external state or I/O")

    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(os, "open", forbidden)
    monkeypatch.setattr(os, "listdir", forbidden)
    monkeypatch.setattr(Path, "read_bytes", forbidden)
    monkeypatch.setattr(Path, "write_bytes", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(time, "time", forbidden)
    monkeypatch.setattr(random, "random", forbidden)
    monkeypatch.setattr(os, "getenv", forbidden)
    parse_runtime_config(data)
    assert data == original


# RC-L0-015
@pytest.mark.parametrize("data", [VALID_BYTES, b"{}", b"{"])
def test_rc_l0_015_repeated_parse_has_value_determinism(data: bytes) -> None:
    assert parse_runtime_config(data) == parse_runtime_config(data)


# RC-L0-016
def test_rc_l0_016_key_order_and_json_whitespace_do_not_change_meaning() -> None:
    first = parse_runtime_config(VALID_BYTES)
    second = parse_runtime_config(b'\n { "data_root" : "data", "config_version" : 1 } \t')
    assert first == second


# RC-L0-017
@pytest.mark.parametrize("data", [b"{", b"{}", config_bytes(config_version=2)])
def test_rc_l0_017_l0_state_and_result_invariants(data: bytes) -> None:
    result = parse_runtime_config(data)
    assert result.state is RuntimeConfigState.INVALID
    assert result.snapshot is None
    assert result.diagnostics
    assert result.state not in {RuntimeConfigState.UNCONFIGURED, RuntimeConfigState.ERROR}


# RC-L1-001
def test_rc_l1_001_explicit_config_is_loaded_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_path = tmp_path / "config.json"
    write_config(config_path)
    reads = 0
    original_read = Path.read_bytes

    def counting_read(path: Path) -> bytes:
        nonlocal reads
        reads += 1
        return original_read(path)

    monkeypatch.setattr(Path, "read_bytes", counting_read)
    assert_l1_success(load_runtime_config(config_path), data_root="data", config_path=config_path)
    assert reads == 1


# RC-L1-002
@pytest.mark.parametrize("missing_parent", [False, True])
def test_rc_l1_002_genuine_absence_is_unconfigured(
    tmp_path: Path,
    missing_parent: bool,
) -> None:
    parent = tmp_path / "missing" if missing_parent else tmp_path
    config_path = parent / "config.json"
    before = set(tmp_path.rglob("*"))
    assert_failure(
        load_runtime_config(config_path),
        RuntimeConfigState.UNCONFIGURED,
        diagnostic(RuntimeConfigDiagnosticCode.CONFIG_NOT_FOUND, None),
    )
    assert set(tmp_path.rglob("*")) == before


# RC-L1-003
def test_rc_l1_003_non_absence_read_failures_are_errors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "config.json"
    write_config(config_path)

    def fail_read(_path: Path) -> bytes:
        raise OSError("injected non-absence read failure")

    monkeypatch.setattr(Path, "read_bytes", fail_read)
    assert_failure(
        load_runtime_config(config_path),
        RuntimeConfigState.ERROR,
        diagnostic(RuntimeConfigDiagnosticCode.CONFIG_READ_ERROR, None),
    )


# RC-L1-004
def test_rc_l1_004_l0_failure_propagates_without_resolution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "config.json"
    write_config(config_path, b"{")
    original_normpath = os.path.normpath

    def reject_resolution(path: str | os.PathLike[str]) -> str:
        value = os.fspath(path)
        if "data" in value:
            raise AssertionError("invalid config reached Data Root resolution")
        return original_normpath(path)

    monkeypatch.setattr(os.path, "normpath", reject_resolution)
    assert_failure(
        load_runtime_config(config_path),
        RuntimeConfigState.INVALID,
        diagnostic(RuntimeConfigDiagnosticCode.MALFORMED_JSON, None),
    )


# RC-L1-005
def test_rc_l1_005_paths_are_absolute_normalized_and_based_on_config_parent(tmp_path: Path) -> None:
    config_path = tmp_path / "nested" / "config.json"
    data_root = "a/../data"
    write_config(config_path, config_bytes(data_root=data_root))
    snapshot = assert_l1_success(
        load_runtime_config(config_path), data_root=data_root, config_path=config_path
    )
    assert snapshot.config_path.is_absolute()
    assert snapshot.data_root_path == lexical(config_path).parent / "data"


# RC-L1-006
def test_rc_l1_006_result_is_independent_of_current_working_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "config.json"
    write_config(config_path, config_bytes(data_root="../data"))
    first = load_runtime_config(config_path)
    other_cwd = tmp_path / "other"
    other_cwd.mkdir()
    monkeypatch.chdir(other_cwd)
    assert load_runtime_config(config_path) == first


# RC-L1-007
def test_rc_l1_007_nonexistent_data_root_is_configured_without_creation(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    target = tmp_path / "missing" / "data"
    write_config(config_path, config_bytes(data_root="missing/data"))
    assert_l1_success(
        load_runtime_config(config_path), data_root="missing/data", config_path=config_path
    )
    assert not target.exists()


# RC-L1-008
@pytest.mark.parametrize("target_kind", ["file", "directory"])
def test_rc_l1_008_data_root_target_type_is_not_queried(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target_kind: str,
) -> None:
    config_path = tmp_path / "config.json"
    target = tmp_path / "target"
    write_config(config_path, config_bytes(data_root="target"))
    target.write_bytes(b"not a directory") if target_kind == "file" else target.mkdir()

    def forbidden_query(_path: Path) -> bool:
        raise AssertionError("queried Data Root target")

    monkeypatch.setattr(Path, "exists", forbidden_query)
    monkeypatch.setattr(Path, "is_dir", forbidden_query)
    monkeypatch.setattr(Path, "is_file", forbidden_query)
    assert_l1_success(load_runtime_config(config_path), data_root="target", config_path=config_path)


# RC-L1-009
def test_rc_l1_009_resolution_is_lexical_and_never_resolves_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "config.json"
    write_config(config_path, config_bytes(data_root="link/../lexical"))

    def forbidden_resolve(_path: Path, *_args: object, **_kwargs: object) -> Path:
        raise AssertionError("canonical target resolution was attempted")

    monkeypatch.setattr(Path, "resolve", forbidden_resolve)
    assert_l1_success(
        load_runtime_config(config_path),
        data_root="link/../lexical",
        config_path=config_path,
    )


def test_native_symlink_auxiliary_preserves_lexical_data_root_path(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    real_target = tmp_path / "real-target"
    real_target.mkdir()
    link = tmp_path / "link"
    try:
        link.symlink_to(real_target, target_is_directory=True)
    except OSError as error:
        pytest.skip(f"native symlink fixture unavailable on this platform: {error}")
    write_config(config_path, config_bytes(data_root="link"))
    snapshot = assert_l1_success(
        load_runtime_config(config_path), data_root="link", config_path=config_path
    )
    assert snapshot.data_root_path == lexical(link)
    assert snapshot.data_root_path != real_target.resolve()


# RC-L1-010, RC-L1-011
def test_rc_l1_010_and_011_guarded_normpath_failure_maps_to_resolution_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "config.json"
    write_config(config_path, config_bytes(data_root=RESOLUTION_FAILURE_MARKER))
    original_normpath = os.path.normpath
    triggered = 0

    def fail_only_marker(path: str | os.PathLike[str]) -> str:
        nonlocal triggered
        if RESOLUTION_FAILURE_MARKER in os.fspath(path):
            triggered += 1
            raise OSError("injected Data Root lexical normalization failure")
        return original_normpath(path)

    monkeypatch.setattr(os.path, "normpath", fail_only_marker)
    assert_failure(
        load_runtime_config(config_path),
        RuntimeConfigState.ERROR,
        diagnostic(RuntimeConfigDiagnosticCode.DATA_ROOT_RESOLUTION_ERROR, "data_root"),
    )
    assert triggered == 1


# RC-L1-012
def test_rc_l1_012_snapshot_is_immutable_and_detached_from_later_file_changes(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.json"
    write_config(config_path)
    snapshot = assert_l1_success(
        load_runtime_config(config_path), data_root="data", config_path=config_path
    )
    write_config(config_path, config_bytes(data_root="changed"))
    assert snapshot.data_root == "data"
    with pytest.raises((AttributeError, TypeError)):
        snapshot.__setattr__("data_root", "mutation")


# RC-L1-013
def test_rc_l1_013_only_the_explicit_file_is_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_path = tmp_path / "config.json"
    fallback_path = tmp_path / "fallback" / "config.json"
    write_config(config_path)
    write_config(fallback_path, config_bytes(data_root="fallback"))
    reads: list[Path] = []
    original_read = Path.read_bytes

    def record_read(path: Path) -> bytes:
        reads.append(path)
        return original_read(path)

    monkeypatch.setattr(Path, "read_bytes", record_read)
    assert_l1_success(load_runtime_config(config_path), data_root="data", config_path=config_path)
    assert reads == [config_path]


# RC-L1-014
@pytest.mark.parametrize("config_path", [Path("config.json"), Path("not-config.json").absolute()])
def test_rc_l1_014_invalid_invocation_is_programmer_error_without_filesystem_access(
    config_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reads = 0

    def forbidden_read(_path: Path) -> bytes:
        nonlocal reads
        reads += 1
        return b""

    monkeypatch.setattr(Path, "read_bytes", forbidden_read)
    with pytest.raises(Exception) as raised:
        load_runtime_config(config_path)
    assert not isinstance(raised.value, RuntimeConfigResult)
    assert reads == 0


# RC-L1-015
@pytest.mark.parametrize("data", [b"{", config_bytes(data_root="")])
def test_rc_l1_015_terminal_failures_do_not_write_or_repair(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    data: bytes,
) -> None:
    config_path = tmp_path / "config.json"
    write_config(config_path, data)
    before = config_path.read_bytes()

    def forbidden_write(_path: Path, _data: bytes) -> int:
        raise AssertionError("terminal failure attempted a write")

    monkeypatch.setattr(Path, "write_bytes", forbidden_write)
    result = load_runtime_config(config_path)
    assert result.state is RuntimeConfigState.INVALID
    assert result.snapshot is None
    assert result.diagnostics
    assert config_path.read_bytes() == before


# RC-L1-016
def test_rc_l1_016_repeated_load_has_value_determinism(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    write_config(config_path, config_bytes(data_root="a/../data"))
    assert load_runtime_config(config_path) == load_runtime_config(config_path)


# RC-X-001
def test_rc_x_001_snapshot_contains_no_runtime_identity_fields() -> None:
    snapshot = assert_l0_success(parse_runtime_config(VALID_BYTES))
    assert vars(snapshot) == {"config_version": 1, "data_root": "data"}


# RC-X-002
def test_rc_x_002_config_api_does_not_terminate_or_launch_upper_layers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("Runtime Config invoked an upper-layer/process action")

    monkeypatch.setattr(os, "abort", forbidden)
    monkeypatch.setattr(os, "_exit", forbidden)
    assert_l0_success(parse_runtime_config(VALID_BYTES))


# RC-X-003
@pytest.mark.parametrize("future_key", ["config_hash", "secret_refs", "governance", "domain"])
def test_rc_x_003_deferred_schema_fields_remain_unknown(future_key: str) -> None:
    data = b'{"config_version":1,"data_root":"data",' + json.dumps(future_key).encode() + b":null}"
    assert_failure(
        parse_runtime_config(data),
        RuntimeConfigState.INVALID,
        diagnostic(RuntimeConfigDiagnosticCode.UNKNOWN_KEY, future_key),
    )


# RC-X-004
def test_rc_x_004_environment_style_source_is_not_a_v0_1_configuration_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ARGUS_HOME", "ignored")
    assert_failure(
        parse_runtime_config(config_bytes(data_root="C:/absolute")),
        RuntimeConfigState.INVALID,
        diagnostic(RuntimeConfigDiagnosticCode.INVALID_DATA_ROOT, "data_root"),
    )
