"""Mutation diagnostics for the corrected S-003/S-004 semantic oracle."""

from __future__ import annotations

import pytest

from ._semantic_boundaries import semantic_boundary_findings


@pytest.mark.parametrize(
    ("mutant", "source", "rule"),
    [
        ("s003_config_path_direct", "def f(c): return c.config_path", "S003_UPSTREAM_CONFIG_PATH"),
        ("s003_config_path_obfuscated", "def f(c): return getattr(c, 'config_' + 'path')", "S003_UPSTREAM_CONFIG_PATH"),
        ("s003_config_alias", "from x import parse_runtime_config as p\ndef f(x): return p(x)", "S003_UPSTREAM_RESOLUTION"),
        ("s003_config_indirect", "from x import load_runtime_config as a\nb=a\ndef f(x): return b(x)", "S003_UPSTREAM_RESOLUTION"),
        ("s003_identity_alias", "from x import resolve_runtime_identity as q\ndef f(x): return q(x)", "S003_UPSTREAM_RESOLUTION"),
        ("s003_dynamic_lookup", "import x\ndef f(v): return getattr(x, 'parse_' + 'runtime_config')(v)", "S003_UPSTREAM_RESOLUTION"),
        ("s003_later_alias", "from x import verify_environment_binding as v\ndef f(x): return v(x)", "S003_LATER_RESPONSIBILITY"),
        ("s003_later_dynamic_lookup", "import x\ndef f(v): return getattr(x, ''.join(['bind_', 'environment']))(v)", "S003_LATER_RESPONSIBILITY"),
        ("s004_cwd_alias", "from os import getcwd as here\ndef f(): return here()", "S004_FORBIDDEN_LOCATOR"),
        ("s004_env_obfuscated", "import os\ndef f(): return getattr(os, 'get' + 'env')('ARGUS_ENV')", "S004_FORBIDDEN_LOCATOR"),
        ("s004_manifest_parent_direct", "def f(artificial_manifest_path, ExpectedEnvironmentBinding): return ExpectedEnvironmentBinding(1, 2, artificial_manifest_path.parent.name)", "S004_DIRECTORY_ENVIRONMENT_FLOW"),
        ("s004_manifest_parent_indirect", "def f(artificial_manifest_path, ExpectedEnvironmentBinding):\n a=artificial_manifest_path.parent\n b=a.name\n return ExpectedEnvironmentBinding(1,2,b)", "S004_DIRECTORY_ENVIRONMENT_FLOW"),
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
