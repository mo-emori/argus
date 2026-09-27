import ctypes
import os
import stat
import tempfile
from ctypes import wintypes
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Protocol, cast

from argus.runtime.data_root_locator import DataRootLocator
from argus.runtime.data_root_marker import (
    DataRootMarker,
    MarkerValidationFailure,
    parse_data_root_marker,
    serialize_data_root_marker,
)
from argus.runtime.environment_binding import (
    BindingFailure,
    BindingFailureClass,
    BindingFailureCode,
    ExpectedEnvironmentBinding,
    VerifiedEnvironmentBinding,
    verify_environment_binding,
)

_MARKER_NAME = "data_root_marker.json"
_ACCESS_DENIED_WINERRORS = frozenset({5, 65})
_DEVICE_UNAVAILABLE_WINERRORS = frozenset({15, 20, 21, 53, 55, 67, 321})
_FILE_NOT_FOUND_WINERRORS = frozenset({2, 3})

_GENERIC_READ = 0x80000000
_DELETE = 0x00010000
_FILE_SHARE_READ = 0x00000001
_FILE_SHARE_WRITE = 0x00000002
_FILE_SHARE_DELETE = 0x00000004
_OPEN_EXISTING = 3
_FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
_FILE_RENAME_INFO_CLASS = 3
_INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value


class _FileRenameInfo(ctypes.Structure):
    _fields_ = [
        ("replace_if_exists", wintypes.BOOL),
        ("root_directory", wintypes.HANDLE),
        ("file_name_length", wintypes.DWORD),
        ("file_name", wintypes.WCHAR * 1),
    ]


class _CreateFileW(Protocol):
    argtypes: list[object]
    restype: object

    def __call__(
        self,
        file_name: str,
        desired_access: int,
        share_mode: int,
        security_attributes: None,
        creation_disposition: int,
        flags_and_attributes: int,
        template_file: None,
    ) -> int | None: ...


class _SetFileInformationByHandle(Protocol):
    argtypes: list[object]
    restype: object

    def __call__(
        self,
        file: int,
        information_class: int,
        file_information: object,
        buffer_size: int,
    ) -> int: ...


class _CloseHandle(Protocol):
    argtypes: list[object]
    restype: object

    def __call__(self, handle: int) -> int: ...


@dataclass(frozen=True)
class LoadedDataRootMarker:
    marker: DataRootMarker
    marker_content_hash: str

    def __post_init__(self) -> None:
        if (
            len(self.marker_content_hash) != 64
            or any(character not in "0123456789abcdef" for character in self.marker_content_hash)
        ):
            raise ValueError("marker_content_hash must be 64 lowercase hexadecimal digits")


@dataclass(frozen=True)
class MarkerInitializationError:
    pass


@dataclass(frozen=True)
class DataRootInitializationUnavailable(MarkerInitializationError):
    pass


@dataclass(frozen=True)
class MarkerAlreadyExists(MarkerInitializationError):
    pass


@dataclass(frozen=True)
class MarkerAtomicWriteFailed(MarkerInitializationError):
    pass


@dataclass(frozen=True)
class MarkerReloadVerificationFailed(MarkerInitializationError):
    pass


def _binding_failure(
    locator: DataRootLocator,
    failure_class: BindingFailureClass,
    code: BindingFailureCode,
) -> BindingFailure:
    return BindingFailure(frozenset({failure_class}), (code,), locator)


def _classify_read_error(
    locator: DataRootLocator,
    error: OSError,
    *,
    marker_open: bool,
) -> BindingFailure:
    winerror = error.winerror
    if winerror in _ACCESS_DENIED_WINERRORS:
        return _binding_failure(
            locator,
            BindingFailureClass.DATA_STORAGE_UNAVAILABLE,
            BindingFailureCode.DATA_ROOT_ACCESS_DENIED,
        )
    if winerror in _DEVICE_UNAVAILABLE_WINERRORS:
        return _binding_failure(
            locator,
            BindingFailureClass.DATA_STORAGE_UNAVAILABLE,
            BindingFailureCode.DEVICE_UNAVAILABLE,
        )
    if marker_open and (
        isinstance(error, FileNotFoundError) or winerror in _FILE_NOT_FOUND_WINERRORS
    ):
        return _binding_failure(
            locator,
            BindingFailureClass.DATA_STORAGE_IDENTITY_MISMATCH,
            BindingFailureCode.MARKER_MISSING,
        )
    if not marker_open and (
        isinstance(error, FileNotFoundError) or winerror in _FILE_NOT_FOUND_WINERRORS
    ):
        return _binding_failure(
            locator,
            BindingFailureClass.DATA_STORAGE_UNAVAILABLE,
            BindingFailureCode.DATA_ROOT_MISSING,
        )
    return _binding_failure(
        locator,
        BindingFailureClass.DATA_STORAGE_UNAVAILABLE,
        BindingFailureCode.MARKER_READ_FAILED,
    )


def _validation_failure(
    locator: DataRootLocator,
    failure: MarkerValidationFailure,
) -> BindingFailure:
    codes = tuple(BindingFailureCode(error.code.value) for error in failure.errors)
    return BindingFailure(
        frozenset({BindingFailureClass.DATA_STORAGE_IDENTITY_MISMATCH}),
        codes,
        locator,
    )


def _read_marker_bytes(path: Path) -> bytes:
    return path.read_bytes()


def load_data_root_marker(
    locator: DataRootLocator,
) -> LoadedDataRootMarker | BindingFailure:
    try:
        root_mode = locator.path.stat().st_mode
    except OSError as error:
        return _classify_read_error(locator, error, marker_open=False)
    if not stat.S_ISDIR(root_mode):
        return _binding_failure(
            locator,
            BindingFailureClass.DATA_STORAGE_UNAVAILABLE,
            BindingFailureCode.MARKER_READ_FAILED,
        )

    try:
        marker_bytes = _read_marker_bytes(locator.path / _MARKER_NAME)
    except OSError as error:
        return _classify_read_error(locator, error, marker_open=True)

    marker = parse_data_root_marker(marker_bytes)
    if isinstance(marker, MarkerValidationFailure):
        return _validation_failure(locator, marker)
    return LoadedDataRootMarker(marker, sha256(marker_bytes).hexdigest())


def load_and_verify_environment_binding(
    locator: DataRootLocator,
    expected: ExpectedEnvironmentBinding,
) -> VerifiedEnvironmentBinding | BindingFailure:
    loaded = load_data_root_marker(locator)
    if isinstance(loaded, BindingFailure):
        return loaded
    return verify_environment_binding(
        locator,
        loaded.marker,
        loaded.marker_content_hash,
        expected,
    )


def _win32_function(name: str) -> object:
    library = ctypes.WinDLL("kernel32", use_last_error=True)
    return library[name]


def _publish_no_replace(temp_path: Path, target_path: Path) -> None:
    create_file = cast(_CreateFileW, _win32_function("CreateFileW"))
    create_file.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    ]
    create_file.restype = wintypes.HANDLE
    set_file_information = cast(
        _SetFileInformationByHandle,
        _win32_function("SetFileInformationByHandle"),
    )
    set_file_information.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        wintypes.LPVOID,
        wintypes.DWORD,
    ]
    set_file_information.restype = wintypes.BOOL
    close_handle = cast(_CloseHandle, _win32_function("CloseHandle"))
    close_handle.argtypes = [wintypes.HANDLE]
    close_handle.restype = wintypes.BOOL

    handle = create_file(
        str(temp_path),
        _GENERIC_READ | _DELETE,
        _FILE_SHARE_READ | _FILE_SHARE_WRITE | _FILE_SHARE_DELETE,
        None,
        _OPEN_EXISTING,
        _FILE_FLAG_BACKUP_SEMANTICS,
        None,
    )
    if handle is None or ctypes.c_void_p(handle).value == _INVALID_HANDLE_VALUE:
        raise ctypes.WinError(ctypes.get_last_error())

    try:
        try:
            target_name = str(target_path)
            target_name_bytes = target_name.encode("utf-16-le")
            header_size = _FileRenameInfo.file_name.offset
            buffer_size = ctypes.sizeof(_FileRenameInfo) + len(target_name_bytes)
            buffer = ctypes.create_string_buffer(buffer_size)
            rename_info = _FileRenameInfo.from_buffer(buffer)
            rename_info.replace_if_exists = False
            rename_info.root_directory = None
            rename_info.file_name_length = len(target_name_bytes)
            ctypes.memmove(
                ctypes.addressof(buffer) + header_size,
                target_name_bytes,
                len(target_name_bytes),
            )
        except (UnicodeEncodeError, MemoryError, OverflowError) as error:
            raise OSError("failed to prepare atomic marker publish") from error

        succeeded = set_file_information(
            handle,
            _FILE_RENAME_INFO_CLASS,
            buffer,
            buffer_size,
        )
        if not succeeded:
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        close_handle(handle)


def _root_available_for_initialization(path: Path) -> bool:
    try:
        return stat.S_ISDIR(path.stat().st_mode)
    except OSError:
        return False


def initialize_data_root_marker(
    locator: DataRootLocator,
    marker: DataRootMarker,
) -> DataRootMarker | MarkerInitializationError:
    if not _root_available_for_initialization(locator.path):
        return DataRootInitializationUnavailable()

    target_path = locator.path / _MARKER_NAME
    try:
        target_path.stat()
    except FileNotFoundError:
        pass
    except OSError:
        return DataRootInitializationUnavailable()
    else:
        return MarkerAlreadyExists()

    marker_bytes = serialize_data_root_marker(marker)
    temp_path: Path | None = None
    published = False
    try:
        descriptor, temp_name = tempfile.mkstemp(
            prefix=".data_root_marker.",
            suffix=".tmp",
            dir=locator.path,
        )
        temp_path = Path(temp_name)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(marker_bytes)
            stream.flush()
            os.fsync(stream.fileno())
        _publish_no_replace(temp_path, target_path)
        published = True
    except OSError:
        if target_path.exists():
            return MarkerAlreadyExists()
        return MarkerAtomicWriteFailed()
    finally:
        if not published and temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass

    reloaded = load_data_root_marker(locator)
    if isinstance(reloaded, BindingFailure) or reloaded.marker != marker:
        return MarkerReloadVerificationFailed()
    return reloaded.marker
