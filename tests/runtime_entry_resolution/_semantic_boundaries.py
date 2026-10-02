"""Semantic boundary analysis used by the corrected S-003/S-004 candidate tests.

The analysis follows imported/copy-assigned callables and simple value flow.  It
intentionally does not reject words such as ``environment`` or ordinary typed
imports: a finding requires a forbidden operation or forbidden data flow.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass


@dataclass(frozen=True)
class BoundaryFinding:
    rule: str
    line: int


_UPSTREAM_OPERATIONS = frozenset(
    {
        "parse_runtime_config",
        "load_runtime_config",
        "resolve_runtime_config",
        "parse_runtime_identity",
        "load_runtime_identity",
        "resolve_runtime_identity",
    }
)
_LATER_OPERATIONS = frozenset(
    {
        "bind_environment",
        "verify_environment_binding",
        "create_result_manifest",
        "write_result_manifest",
    }
)
_DYNAMIC_EXECUTION = frozenset({"__import__", "eval", "exec", "compile"})
_LOCATOR_OPERATIONS = frozenset(
    {
        "os.getcwd",
        "os.chdir",
        "os.getenv",
        "os.walk",
        "pathlib.Path.cwd",
        "pathlib.Path.glob",
        "pathlib.Path.rglob",
    }
)


def _dotted(node: ast.AST, aliases: dict[str, str]) -> str | None:
    if isinstance(node, ast.Name):
        return aliases.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        base = _dotted(node.value, aliases)
        return f"{base}.{node.attr}" if base else None
    return None


def _constant_text(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = _constant_text(node.left), _constant_text(node.right)
        return left + right if left is not None and right is not None else None
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "join"
        and _constant_text(node.func.value) is not None
        and len(node.args) == 1
    ):
        separator = _constant_text(node.func.value)
        values = node.args[0]
        if isinstance(values, (ast.List, ast.Tuple)):
            parts = [_constant_text(item) for item in values.elts]
            if separator is not None and all(part is not None for part in parts):
                return separator.join(part for part in parts if part is not None)
    if isinstance(node, (ast.List, ast.Tuple)):
        parts = [_constant_text(item) for item in node.elts]
        if any(part is None for part in parts):
            return None
        return "".join(part for part in parts if part is not None)
    return None


def semantic_boundary_findings(source: str) -> tuple[BoundaryFinding, ...]:
    tree = ast.parse(source)
    aliases: dict[str, str] = {}
    tainted: set[str] = set()
    findings: list[BoundaryFinding] = []

    def called_name(node: ast.AST) -> str:
        dotted = _dotted(node, aliases)
        if dotted:
            return dotted
        if (
            isinstance(node, ast.Call)
            and _dotted(node.func, aliases) in {"getattr", "builtins.getattr"}
            and len(node.args) >= 2
        ):
            owner = _dotted(node.args[0], aliases)
            attribute = _constant_text(node.args[1])
            if owner and attribute:
                return f"{owner}.{attribute}"
        return ""

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for item in node.names:
                aliases[item.asname or item.name.split(".")[0]] = item.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            for item in node.names:
                aliases[item.asname or item.name] = f"{node.module}.{item.name}"

    def is_locator_value(node: ast.AST) -> bool:
        if isinstance(node, ast.Name):
            return node.id in tainted
        dotted = _dotted(node, aliases) or ""
        if dotted == "artificial_manifest_path" or dotted.startswith("artificial_manifest_path."):
            return any(
                part in dotted.split(".")
                for part in ("parent", "parents", "stem", "parts", "anchor")
            )
        if isinstance(node, ast.Call):
            called = called_name(node.func)
            if called in _LOCATOR_OPERATIONS or called.endswith(".resolve"):
                return True
            return any(is_locator_value(arg) for arg in node.args)
        if isinstance(node, (ast.Attribute, ast.Subscript, ast.Compare, ast.BoolOp, ast.IfExp)):
            return any(is_locator_value(child) for child in ast.iter_child_nodes(node))
        return False

    # Fixed-point propagation handles innocuous renaming and several layers of indirection.
    changed = True
    while changed:
        changed = False
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                value = node.value
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                if value is not None and is_locator_value(value):
                    for target in targets:
                        if isinstance(target, ast.Name) and target.id not in tainted:
                            tainted.add(target.id)
                            changed = True
                dotted = _dotted(value, aliases) if value is not None else None
                if dotted:
                    for target in targets:
                        if isinstance(target, ast.Name):
                            aliases.setdefault(target.id, dotted)

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "config_path":
            findings.append(BoundaryFinding("S003_UPSTREAM_CONFIG_PATH", node.lineno))
        if not isinstance(node, ast.Call):
            continue
        called = called_name(node.func)
        leaf = called.rsplit(".", 1)[-1]
        if leaf in _DYNAMIC_EXECUTION:
            findings.append(BoundaryFinding("S003_DYNAMIC_EXECUTION", node.lineno))
        if leaf in _UPSTREAM_OPERATIONS:
            findings.append(BoundaryFinding("S003_UPSTREAM_RESOLUTION", node.lineno))
        if leaf in _LATER_OPERATIONS:
            findings.append(BoundaryFinding("S003_LATER_RESPONSIBILITY", node.lineno))
        if called in _LOCATOR_OPERATIONS:
            findings.append(BoundaryFinding("S004_FORBIDDEN_LOCATOR", node.lineno))
        if leaf == "getattr" and len(node.args) >= 2:
            attribute = _constant_text(node.args[1])
            owner = _dotted(node.args[0], aliases) or ""
            if attribute == "config_path":
                findings.append(BoundaryFinding("S003_UPSTREAM_CONFIG_PATH", node.lineno))
            if owner in {"os", "os.environ"} or attribute in {"getcwd", "getenv", "walk"}:
                findings.append(BoundaryFinding("S004_FORBIDDEN_LOCATOR", node.lineno))
        if leaf in {"ExpectedEnvironmentBinding", "_ExpectedBinding"}:
            environment_arg = (
                node.keywords[-1].value
                if node.keywords and node.keywords[-1].arg == "environment"
                else node.args[2]
                if len(node.args) >= 3
                else None
            )
            if environment_arg is not None and is_locator_value(environment_arg):
                findings.append(BoundaryFinding("S004_DIRECTORY_ENVIRONMENT_FLOW", node.lineno))

    return tuple(sorted(set(findings), key=lambda item: (item.line, item.rule)))
