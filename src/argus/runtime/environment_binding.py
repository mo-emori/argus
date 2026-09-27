import re
from dataclasses import dataclass
from enum import Enum
from typing import cast
from uuid import UUID

from argus.runtime.data_root_locator import DataRootLocator
from argus.runtime.data_root_marker import DataRootMarker
from argus.runtime.environment import Environment

_MARKER_CONTENT_HASH_PATTERN = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True)
class ExpectedEnvironmentBinding:
    state_id: UUID
    data_root_id: UUID
    environment: Environment

    def __post_init__(self) -> None:
        _validate_expected_binding(self.state_id, self.data_root_id, self.environment)


def _validate_expected_binding(
    state_id: object,
    data_root_id: object,
    environment: object,
) -> None:
    if not isinstance(state_id, UUID) or state_id.version != 4:
        raise ValueError("state_id must be a UUID v4")
    if not isinstance(data_root_id, UUID) or data_root_id.version != 4:
        raise ValueError("data_root_id must be a UUID v4")
    if not isinstance(environment, Environment):
        raise TypeError("environment must be an Environment")


class BindingFailureClass(str, Enum):
    DATA_STORAGE_UNAVAILABLE = "DATA_STORAGE_UNAVAILABLE"
    DATA_STORAGE_IDENTITY_MISMATCH = "DATA_STORAGE_IDENTITY_MISMATCH"
    ENVIRONMENT_BINDING_MISMATCH = "ENVIRONMENT_BINDING_MISMATCH"


class BindingFailureCode(str, Enum):
    DATA_ROOT_MISSING = "DATA_ROOT_MISSING"
    DATA_ROOT_ACCESS_DENIED = "DATA_ROOT_ACCESS_DENIED"
    DEVICE_UNAVAILABLE = "DEVICE_UNAVAILABLE"
    MARKER_READ_FAILED = "MARKER_READ_FAILED"
    MARKER_MISSING = "MARKER_MISSING"
    MALFORMED_JSON = "MALFORMED_JSON"
    JSON_ROOT_NOT_OBJECT = "JSON_ROOT_NOT_OBJECT"
    MISSING_FIELD = "MISSING_FIELD"
    UNKNOWN_FIELD = "UNKNOWN_FIELD"
    DUPLICATE_FIELD = "DUPLICATE_FIELD"
    INVALID_FIELD_TYPE = "INVALID_FIELD_TYPE"
    UNSUPPORTED_SCHEMA_VERSION = "UNSUPPORTED_SCHEMA_VERSION"
    INVALID_STATE_ID = "INVALID_STATE_ID"
    INVALID_DATA_ROOT_ID = "INVALID_DATA_ROOT_ID"
    INVALID_ENVIRONMENT = "INVALID_ENVIRONMENT"
    INVALID_CREATED_AT = "INVALID_CREATED_AT"
    STATE_ID_MISMATCH = "STATE_ID_MISMATCH"
    DATA_ROOT_ID_MISMATCH = "DATA_ROOT_ID_MISMATCH"
    ENVIRONMENT_MISMATCH = "ENVIRONMENT_MISMATCH"


@dataclass(frozen=True)
class BindingFailure:
    failure_classes: frozenset[BindingFailureClass]
    codes: tuple[BindingFailureCode, ...]
    locator: DataRootLocator

    def __post_init__(self) -> None:
        _validate_binding_failure(self.failure_classes, self.codes, self.locator)


def _validate_binding_failure(
    failure_classes: object,
    codes: object,
    locator: object,
) -> None:
    if not isinstance(failure_classes, frozenset):
        raise TypeError("failure_classes must be a frozenset")
    if not failure_classes:
        raise ValueError("failure_classes must not be empty")
    typed_failure_classes = cast(frozenset[object], failure_classes)
    if not all(
        isinstance(failure_class, BindingFailureClass)
        for failure_class in typed_failure_classes
    ):
        raise TypeError("failure_classes must contain BindingFailureClass values")
    if not isinstance(codes, tuple):
        raise TypeError("codes must be a tuple")
    if not codes:
        raise ValueError("codes must not be empty")
    typed_codes = cast(tuple[object, ...], codes)
    if not all(isinstance(code, BindingFailureCode) for code in typed_codes):
        raise TypeError("codes must contain BindingFailureCode values")
    if not isinstance(locator, DataRootLocator):
        raise TypeError("locator must be a DataRootLocator")


@dataclass(frozen=True)
class VerifiedEnvironmentBinding:
    expected: ExpectedEnvironmentBinding
    marker: DataRootMarker
    locator: DataRootLocator
    marker_content_hash: str

    def __post_init__(self) -> None:
        _validate_verified_binding(
            self.expected,
            self.marker,
            self.locator,
            self.marker_content_hash,
        )


def _validate_verified_binding(
    expected: object,
    marker: object,
    locator: object,
    marker_content_hash: object,
) -> None:
    if not isinstance(expected, ExpectedEnvironmentBinding):
        raise TypeError("expected must be an ExpectedEnvironmentBinding")
    if not isinstance(marker, DataRootMarker):
        raise TypeError("marker must be a DataRootMarker")
    if not isinstance(locator, DataRootLocator):
        raise TypeError("locator must be a DataRootLocator")
    if not isinstance(marker_content_hash, str):
        raise TypeError("marker_content_hash must be a string")
    if _MARKER_CONTENT_HASH_PATTERN.fullmatch(marker_content_hash) is None:
        raise ValueError("marker_content_hash must be 64 lowercase hexadecimal digits")


def verify_environment_binding(
    locator: DataRootLocator,
    marker: DataRootMarker,
    marker_content_hash: str,
    expected: ExpectedEnvironmentBinding,
) -> VerifiedEnvironmentBinding | BindingFailure:
    failure_classes: set[BindingFailureClass] = set()
    codes: list[BindingFailureCode] = []

    if marker.state_id != expected.state_id:
        failure_classes.add(BindingFailureClass.ENVIRONMENT_BINDING_MISMATCH)
        codes.append(BindingFailureCode.STATE_ID_MISMATCH)

    if marker.data_root_id != expected.data_root_id:
        failure_classes.add(BindingFailureClass.DATA_STORAGE_IDENTITY_MISMATCH)
        codes.append(BindingFailureCode.DATA_ROOT_ID_MISMATCH)

    if marker.environment != expected.environment:
        failure_classes.add(BindingFailureClass.ENVIRONMENT_BINDING_MISMATCH)
        codes.append(BindingFailureCode.ENVIRONMENT_MISMATCH)

    if codes:
        return BindingFailure(
            failure_classes=frozenset(failure_classes),
            codes=tuple(codes),
            locator=locator,
        )

    return VerifiedEnvironmentBinding(
        expected=expected,
        marker=marker,
        locator=locator,
        marker_content_hash=marker_content_hash,
    )
