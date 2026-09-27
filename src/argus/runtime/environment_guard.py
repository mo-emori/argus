import ntpath
from dataclasses import dataclass
from enum import Enum
from pathlib import Path, PureWindowsPath
from typing import ClassVar

from argus.runtime.data_root_locator import DataRootLocator
from argus.runtime.data_root_marker_store import load_and_verify_environment_binding
from argus.runtime.environment import Environment
from argus.runtime.environment_binding import (
    BindingFailure,
    ExpectedEnvironmentBinding,
    VerifiedEnvironmentBinding,
)


class TestEnvironmentGuardFailureCode(str, Enum):
    __test__ = False

    TEST_ENVIRONMENT_REQUIRED = "TEST_ENVIRONMENT_REQUIRED"


@dataclass(frozen=True)
class TestEnvironmentGuardFailure:
    __test__: ClassVar[bool] = False

    code: TestEnvironmentGuardFailureCode
    locator: DataRootLocator


class WriteTargetPathFailureCode(str, Enum):
    INVALID_VERIFIED_ROOT = "INVALID_VERIFIED_ROOT"
    EMPTY_PATH = "EMPTY_PATH"
    ABSOLUTE_PATH = "ABSOLUTE_PATH"
    DRIVE_QUALIFIED_PATH = "DRIVE_QUALIFIED_PATH"
    UNC_PATH = "UNC_PATH"
    DEVICE_NAMESPACE_PATH = "DEVICE_NAMESPACE_PATH"
    PARENT_TRAVERSAL = "PARENT_TRAVERSAL"
    SELF_REFERENCE = "SELF_REFERENCE"
    ALTERNATE_DATA_STREAM = "ALTERNATE_DATA_STREAM"
    RESERVED_DEVICE_NAME = "RESERVED_DEVICE_NAME"
    TRAILING_DOT_OR_SPACE = "TRAILING_DOT_OR_SPACE"
    INVALID_CHARACTER = "INVALID_CHARACTER"


@dataclass(frozen=True)
class WriteTargetPathFailure:
    code: WriteTargetPathFailureCode
    relative_path: str


@dataclass(frozen=True)
class ResolvedWriteTarget:
    binding: VerifiedEnvironmentBinding
    relative_path: PureWindowsPath
    target_path: Path


_INVALID_CHARACTERS = frozenset('<>"|?*\x00')
_RESERVED_DEVICE_NAMES = frozenset(
    {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{number}" for number in range(1, 10)),
        *(f"LPT{number}" for number in range(1, 10)),
    }
)


def verify_test_environment_startup(
    locator: DataRootLocator,
    expected: ExpectedEnvironmentBinding,
) -> VerifiedEnvironmentBinding | BindingFailure | TestEnvironmentGuardFailure:
    if expected.environment is not Environment.TEST:
        return TestEnvironmentGuardFailure(
            code=TestEnvironmentGuardFailureCode.TEST_ENVIRONMENT_REQUIRED,
            locator=locator,
        )
    return load_and_verify_environment_binding(locator, expected)


def _path_failure(
    code: WriteTargetPathFailureCode,
    relative_path: str,
) -> WriteTargetPathFailure:
    return WriteTargetPathFailure(code=code, relative_path=relative_path)


def _validate_relative_path(
    relative_path: str,
) -> tuple[str, ...] | WriteTargetPathFailure:
    if relative_path == "":
        return _path_failure(WriteTargetPathFailureCode.EMPTY_PATH, relative_path)

    normalized = relative_path.replace("/", "\\")
    if normalized.startswith(("\\\\?\\", "\\\\.\\")):
        return _path_failure(
            WriteTargetPathFailureCode.DEVICE_NAMESPACE_PATH,
            relative_path,
        )
    if normalized.startswith("\\\\"):
        return _path_failure(WriteTargetPathFailureCode.UNC_PATH, relative_path)

    drive, tail = ntpath.splitdrive(normalized)
    if drive:
        code = (
            WriteTargetPathFailureCode.ABSOLUTE_PATH
            if tail.startswith("\\")
            else WriteTargetPathFailureCode.DRIVE_QUALIFIED_PATH
        )
        return _path_failure(code, relative_path)
    if normalized.startswith("\\"):
        return _path_failure(WriteTargetPathFailureCode.ABSOLUTE_PATH, relative_path)

    components = tuple(normalized.split("\\"))
    if ".." in components:
        return _path_failure(
            WriteTargetPathFailureCode.PARENT_TRAVERSAL,
            relative_path,
        )
    if "." in components:
        return _path_failure(
            WriteTargetPathFailureCode.SELF_REFERENCE,
            relative_path,
        )
    if "" in components:
        return _path_failure(WriteTargetPathFailureCode.EMPTY_PATH, relative_path)

    for component in components:
        if any(character in _INVALID_CHARACTERS for character in component):
            return _path_failure(
                WriteTargetPathFailureCode.INVALID_CHARACTER,
                relative_path,
            )
        if ":" in component:
            return _path_failure(
                WriteTargetPathFailureCode.ALTERNATE_DATA_STREAM,
                relative_path,
            )
        if component.endswith((".", " ")):
            return _path_failure(
                WriteTargetPathFailureCode.TRAILING_DOT_OR_SPACE,
                relative_path,
            )
        if component.split(".", maxsplit=1)[0].upper() in _RESERVED_DEVICE_NAMES:
            return _path_failure(
                WriteTargetPathFailureCode.RESERVED_DEVICE_NAME,
                relative_path,
            )

    return components


def resolve_test_write_target(
    locator: DataRootLocator,
    expected: ExpectedEnvironmentBinding,
    relative_path: str,
) -> (
    ResolvedWriteTarget
    | BindingFailure
    | TestEnvironmentGuardFailure
    | WriteTargetPathFailure
):
    components = _validate_relative_path(relative_path)
    if isinstance(components, WriteTargetPathFailure):
        return components

    if expected.environment is not Environment.TEST:
        return TestEnvironmentGuardFailure(
            code=TestEnvironmentGuardFailureCode.TEST_ENVIRONMENT_REQUIRED,
            locator=locator,
        )

    binding = load_and_verify_environment_binding(locator, expected)
    if isinstance(binding, BindingFailure):
        return binding

    root = binding.locator.path
    root_text = str(root)
    if not ntpath.isabs(root_text):
        return _path_failure(
            WriteTargetPathFailureCode.INVALID_VERIFIED_ROOT,
            relative_path,
        )

    target = root.joinpath(*components)
    normalized_root = ntpath.normcase(ntpath.normpath(root_text))
    normalized_target = ntpath.normcase(ntpath.normpath(str(target)))
    try:
        contained = ntpath.commonpath((normalized_root, normalized_target)) == normalized_root
    except ValueError:
        contained = False
    if not contained:
        return _path_failure(
            WriteTargetPathFailureCode.PARENT_TRAVERSAL,
            relative_path,
        )

    return ResolvedWriteTarget(
        binding=binding,
        relative_path=PureWindowsPath(*components),
        target_path=target,
    )
