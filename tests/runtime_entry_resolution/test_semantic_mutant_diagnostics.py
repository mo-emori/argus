"""Mutation diagnostics for the corrected S-003/S-004 semantic oracle."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass, make_dataclass
from types import ModuleType
from typing import Any, cast

import pytest

from ._semantic_boundaries import semantic_boundary_findings
from ._semantic_observer import (
    byte_snapshot,
    observe_call_attempt,
    observe_calls,
    public_type_contract_violations,
)


def _through_local_wrapper() -> object:
    imported = __import__("importlib").import_module
    return imported("math")


@pytest.mark.parametrize(
    ("mutant", "source", "rule"),
    [
        ("s003_config_path_direct", "def f(c): return c.config_path", "S003_UPSTREAM_CONFIG_PATH"),
        (
            "s003_config_path_obfuscated",
            "def f(c): return getattr(c, 'config_' + 'path')",
            "S003_UPSTREAM_CONFIG_PATH",
        ),
        (
            "s003_config_alias",
            "from x import parse_runtime_config as p\ndef f(x): return p(x)",
            "S003_UPSTREAM_RESOLUTION",
        ),
        (
            "s003_config_indirect",
            "from x import load_runtime_config as a\nb=a\ndef f(x): return b(x)",
            "S003_UPSTREAM_RESOLUTION",
        ),
        (
            "s003_identity_alias",
            "from x import resolve_runtime_identity as q\ndef f(x): return q(x)",
            "S003_UPSTREAM_RESOLUTION",
        ),
        (
            "s003_dynamic_lookup",
            "import x\ndef f(v): return getattr(x, 'parse_' + 'runtime_config')(v)",
            "S003_UPSTREAM_RESOLUTION",
        ),
        (
            "s003_later_alias",
            "from x import verify_environment_binding as v\ndef f(x): return v(x)",
            "S003_LATER_RESPONSIBILITY",
        ),
        (
            "s003_later_dynamic_lookup",
            "import x\ndef f(v): return getattr(x, ''.join(['bind_', 'environment']))(v)",
            "S003_LATER_RESPONSIBILITY",
        ),
        (
            "s004_cwd_alias",
            "from os import getcwd as here\ndef f(): return here()",
            "S004_FORBIDDEN_LOCATOR",
        ),
        (
            "s004_env_obfuscated",
            "import os\ndef f(): return getattr(os, 'get' + 'env')('ARGUS_ENV')",
            "S004_FORBIDDEN_LOCATOR",
        ),
        (
            "s004_manifest_parent_direct",
            "def f(artificial_manifest_path, ExpectedEnvironmentBinding): return ExpectedEnvironmentBinding(1, 2, artificial_manifest_path.parent.name)",
            "S004_DIRECTORY_ENVIRONMENT_FLOW",
        ),
        (
            "s004_manifest_parent_indirect",
            "def f(artificial_manifest_path, ExpectedEnvironmentBinding):\n a=artificial_manifest_path.parent\n b=a.name\n return ExpectedEnvironmentBinding(1,2,b)",
            "S004_DIRECTORY_ENVIRONMENT_FLOW",
        ),
    ],
)
def test_corrected_semantic_oracle_rejects_mutant(mutant: str, source: str, rule: str) -> None:
    del mutant
    assert rule in {finding.rule for finding in semantic_boundary_findings(source)}


def test_corrected_semantic_oracle_allows_typed_legitimate_python() -> None:
    source = """
from argus.runtime.environment_binding import ExpectedEnvironmentBinding
from argus.runtime.runtime_identity import RuntimeIdentity
def f(identity: RuntimeIdentity) -> ExpectedEnvironmentBinding:
    return ExpectedEnvironmentBinding(identity.state_id, identity.data_root_id, identity.environment)
"""
    assert semantic_boundary_findings(source) == ()


@pytest.mark.parametrize(
    "factory",
    [
        lambda: __import__("importlib").import_module("math"),
        _through_local_wrapper,
        lambda: getattr(__import__("importlib"), "import_" + "module")("math"),
    ],
    ids=["from-import-equivalent", "local-wrapper", "dynamic-lookup"],
)
def test_v03_observer_rejects_import_execution_variants(factory: Any) -> None:
    _, events = observe_calls(factory)
    assert any(event.endswith(".import_module") for event in events)


def test_v03_observer_violation_is_controlled_not_callback_exception() -> None:
    result, events = observe_calls(lambda: __import__("importlib").import_module("math"))
    assert result is not None
    assert events


@pytest.mark.parametrize(
    ("module_name", "function_name"),
    [
        ("argus.runtime.runtime_config", "load_runtime_config"),
        ("argus.runtime.runtime_config", "parse_runtime_config"),
        ("argus.runtime.runtime_identity", "load_runtime_identity"),
        ("argus.runtime.environment_binding", "verify_environment_binding"),
        ("argus.runtime.data_root_marker_store", "initialize_data_root_marker"),
    ],
)
def test_v03_observer_rejects_boundary_alias_and_wrapper_calls(
    module_name: str, function_name: str
) -> None:
    namespace: dict[str, Any] = {"__name__": module_name}
    exec(f"def {function_name}(): return 'called'", namespace)  # noqa: S102 - diagnostic mutant
    boundary = namespace[function_name]

    def local_wrapper() -> object:
        alias = boundary
        return alias()

    _, events = observe_calls(local_wrapper, forbidden_callables=(boundary,))
    assert events == (f"{module_name}.{function_name}",)


@pytest.mark.parametrize("target_name", ["manifest.json", "__init__.py", "marker.json"])
def test_v03_byte_observer_rejects_actual_write_mutants(tmp_path: Any, target_name: str) -> None:
    target = tmp_path / target_name
    target.write_bytes(b"before")
    before = byte_snapshot((target,))
    target.write_bytes(b"after")
    assert byte_snapshot((target,)) != before


def _legitimate_shape_module(style: str) -> ModuleType:
    """Build the same public semantics through three genuinely distinct forms."""

    module = ModuleType(f"shape_{style}")
    specifications = {
        "RuntimeEntryResolutionDiagnostic": (("code", object), ("field_name", object)),
        "RuntimeEntryResolutionFailure": (("diagnostic", object),),
        "ResolvedPythonModuleTarget": (("kind", object), ("module_name", object), ("origin_path", object)),
        "RuntimeEntryResolutionResult": (("startup_target", object), ("expected_binding", object), ("data_root_locator", object)),
    }
    if style == "decorated-class":
        @dataclass(frozen=True)
        class RuntimeEntryResolutionDiagnostic:
            code: object
            field_name: object

        @dataclass(frozen=True)
        class RuntimeEntryResolutionFailure:
            diagnostic: object

        @dataclass(frozen=True)
        class ResolvedPythonModuleTarget:
            kind: object
            module_name: object
            origin_path: object

        @dataclass(frozen=True)
        class RuntimeEntryResolutionResult:
            startup_target: object
            expected_binding: object
            data_root_locator: object

        for value in (
            RuntimeEntryResolutionDiagnostic,
            RuntimeEntryResolutionFailure,
            ResolvedPythonModuleTarget,
            RuntimeEntryResolutionResult,
        ):
            value.__module__ = module.__name__
            setattr(module, value.__name__, value)
    elif style == "factory":
        for name, specification in specifications.items():
            value = make_dataclass(name, list(specification), frozen=True)
            value.__module__ = module.__name__
            setattr(module, name, value)
    elif style == "namespace-assignment":
        for name, specification in specifications.items():
            namespace = {"__annotations__": dict(specification), "__module__": module.__name__}
            setattr(module, name, dataclass(frozen=True)(type(name, (), namespace)))
    else:
        raise AssertionError(style)
    return module


def _shape_module(*, violation: str) -> ModuleType:
    module = ModuleType(f"shape_violation_{violation}")
    definitions = {
        "RuntimeEntryResolutionDiagnostic": (("code", object), ("field_name", object)),
        "RuntimeEntryResolutionFailure": (("diagnostic", object),),
        "ResolvedPythonModuleTarget": (
            ("kind", object),
            ("module_name", object),
            ("origin_path", object),
        ),
        "RuntimeEntryResolutionResult": (
            ("startup_target", object),
            ("expected_binding", object),
            ("data_root_locator", object),
        ),
    }
    for name, specification in definitions.items():
        fields_spec = list(specification)
        frozen = True
        if violation == "mutable" and name == "RuntimeEntryResolutionResult":
            frozen = False
        if violation == "missing-field" and name == "RuntimeEntryResolutionResult":
            fields_spec.pop()
        if violation == "extra-field" and name == "RuntimeEntryResolutionResult":
            fields_spec.append(("extra", object))
        value = make_dataclass(name, fields_spec, frozen=frozen)
        value.__module__ = module.__name__
        setattr(module, name, value)
    if violation == "not-dataclass":
        vars(module)["RuntimeEntryResolutionFailure"] = type(
            "RuntimeEntryResolutionFailure", (), {}
        )
        vars(module)["RuntimeEntryResolutionFailure"].__module__ = module.__name__
    elif violation == "non-local":
        module.RuntimeEntryResolutionFailure.__module__ = "foreign"
    elif violation == "renamed":
        delattr(module, "RuntimeEntryResolutionFailure")
    elif violation == "wrong-order":
        value = make_dataclass(
            "RuntimeEntryResolutionResult",
            [
                ("expected_binding", object),
                ("startup_target", object),
                ("data_root_locator", object),
            ],
            frozen=True,
        )
        value.__module__ = module.__name__
        vars(module)["RuntimeEntryResolutionResult"] = value
    return module


@pytest.mark.parametrize("style", ["decorated-class", "factory", "namespace-assignment"])
def test_v03_public_shape_accepts_three_legitimate_construction_forms(style: str) -> None:
    module = _legitimate_shape_module(style)
    constructed = module.RuntimeEntryResolutionDiagnostic("code", "field")
    assert (constructed.code, constructed.field_name) == ("code", "field")
    assert public_type_contract_violations(module) == ()


@pytest.mark.parametrize(
    "violation",
    ["mutable", "missing-field", "extra-field", "not-dataclass", "non-local", "wrong-order"],
)
def test_v03_public_shape_rejects_six_semantic_violations(violation: str) -> None:
    assert public_type_contract_violations(_shape_module(violation=violation))


def test_v03_observer_does_not_false_red_same_named_unrelated_callable() -> None:
    namespace: dict[str, Any] = {"__name__": "argus.runtime.runtime_config"}
    exec("def load_runtime_config(): return 'unrelated'", namespace)  # noqa: S102
    result, events = observe_calls(namespace["load_runtime_config"])
    assert result == "unrelated"
    assert events == ()


def test_v03_observer_installation_removal_preserves_existing_profiler() -> None:
    previous = sys.getprofile()
    seen: list[str] = []

    def sentinel(frame: Any, event: str, arg: Any) -> None:
        if event == "call" and frame.f_code is _through_local_wrapper.__code__:
            seen.append(event)

    sys.setprofile(sentinel)
    try:
        result, events = observe_calls(lambda: 41 + 1)
        assert result == 42
        assert events == ()
        assert sys.getprofile() is sentinel
        _through_local_wrapper()
        assert seen == ["call"]
    finally:
        sys.setprofile(previous)


def test_v03_observer_restores_profiler_when_operation_raises() -> None:
    previous = sys.getprofile()

    def explode() -> object:
        raise RuntimeError("control")

    with pytest.raises(RuntimeError, match="control"):
        observe_calls(explode)
    assert sys.getprofile() is previous


def test_v03_from_import_import_module_bypass_is_rejected() -> None:
    from importlib import import_module as imported

    _, events = observe_calls(lambda: imported("math"))
    assert events == ("importlib.import_module",)


def test_v03_from_import_popen_launch_is_rejected() -> None:
    from subprocess import Popen as imported_popen

    process = None
    try:
        value, events = observe_calls(
            lambda: imported_popen(
                [sys.executable, "-c", "pass"],
                stdout=-1,
                stderr=-1,
            )
        )
        assert any(event.endswith("Popen.__init__") for event in events)
        assert any(event.endswith("Popen._execute_child") for event in events)
        process = cast(subprocess.Popen[bytes], value)
    finally:
        if process is not None:
            process.communicate(timeout=10)


def test_v03_manifest_write_after_failure_is_rejected(tmp_path: Any) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_bytes(b"{")
    before = byte_snapshot((manifest,))
    try:
        raise ValueError("terminal failure")
    except ValueError:
        manifest.write_bytes(b"mutated-after-failure")
    assert byte_snapshot((manifest,)) != before


def test_v03_spy_triggered_failure_is_controlled() -> None:
    def boundary() -> object:
        raise LookupError("spy failure")

    result, error, events = observe_call_attempt(
        boundary, forbidden_callables=(boundary,)
    )
    assert result is None
    assert isinstance(error, LookupError)
    assert str(error) == "spy failure"
    assert events == (f"{__name__}.test_v03_spy_triggered_failure_is_controlled.<locals>.boundary",)


@pytest.mark.parametrize("wrong_outcome", [None, "failure", object()], ids=["none", "failure", "alien"])
def test_v03_exact_success_oracle_rejects_wrong_outcomes(wrong_outcome: object) -> None:
    expected = ("PYTHON_MODULE", "pkg", "/absolute/pkg/__init__.py", "TEST")
    assert wrong_outcome != expected
