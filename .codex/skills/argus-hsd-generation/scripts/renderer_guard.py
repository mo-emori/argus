from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

LEGACY_MODULES = {"full_writer", "drift_load_poc", "multi_section_poc", "repair_34", "writer_poc"}
FORBIDDEN_FUNCTIONS = {"render_context", "make_plan"}
FIXED_BODY_NAMES = {"SECTION", "SECTIONS"}
ROLE_EXEMPT = {"render_planning.py", "renderer_guard.py", "human_facing_gate.py"}


@dataclass(frozen=True)
class RendererFinding:
    path: str
    code: str
    detail: str


def scan_script(path: Path) -> list[RendererFinding]:
    source = path.read_text("utf-8")
    tree = ast.parse(source)
    findings: list[RendererFinding] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            modules = [alias.name.split(".")[0] for alias in node.names]
            if isinstance(node, ast.ImportFrom) and node.module:
                modules.append(node.module.split(".")[0])
            for module in LEGACY_MODULES.intersection(modules):
                findings.append(RendererFinding(str(path), "LEGACY_RENDERER_IMPORT", module))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in FORBIDDEN_FUNCTIONS:
            findings.append(RendererFinding(str(path), "HUMAN_RENDERER_FUNCTION", node.name))
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = {target.id for target in targets if isinstance(target, ast.Name)}
            value = node.value
            if names & FIXED_BODY_NAMES and isinstance(value, (ast.Constant, ast.Dict)):
                findings.append(RendererFinding(str(path), "FIXED_SECTION_BODY", ",".join(sorted(names))))
    if path.name not in ROLE_EXEMPT and "```mermaid" in source and ("flowchart" in source or "graph " in source):
        findings.append(RendererFinding(str(path), "GENERIC_MERMAID_GENERATOR", path.name))
    if path.name != "renderer_guard.py" and "tests/fixtures/legacy-renderers" in source.replace("\\", "/"):
        findings.append(RendererFinding(str(path), "LEGACY_FIXTURE_EXECUTION", path.name))
    return findings


def scan_active_scripts(root: Path) -> list[RendererFinding]:
    findings: list[RendererFinding] = []
    for path in sorted(root.rglob("*.py")):
        findings.extend(scan_script(path))
    return findings
