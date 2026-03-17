#!/usr/bin/env python3
"""
Generate two Markdown files at the project root:

- STRUCTURE.md
- API_DOCSTRINGS.md

Custom filtering:
- .projectdocsignore : paths/patterns to exclude
- .projectdocskeep   : paths/patterns to force-include

Precedence:
- keep rules override ignore rules

Run from the project root:
    python scripts/generate_project_docs.py
"""

from __future__ import annotations

import ast
import fnmatch
from pathlib import Path
from typing import Iterable


STRUCTURE_OUTPUT = "STRUCTURE.md"
API_OUTPUT = "API_DOCSTRINGS.md"
IGNORE_FILE = ".projectdocsignore"
KEEP_FILE = ".projectdocskeep"


def load_patterns(file_path: Path) -> list[str]:
    if not file_path.exists():
        return []

    patterns: list[str] = []
    for line in file_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


def normalize_rel_path(path: Path, project_root: Path) -> str:
    rel = path.relative_to(project_root).as_posix()
    if path.is_dir():
        return rel + "/"
    return rel


def matches_pattern(rel_path: str, patterns: list[str], is_dir: bool) -> bool:
    """
    Supports:
    - exact paths: src/utils/paths.py
    - directory paths: backup-mac-tese/
    - glob patterns: *.egg-info, *.log, backup-*
    - recursive globs via fnmatch semantics
    """
    for pattern in patterns:
        pattern = pattern.strip()
        if not pattern:
            continue

        # Directory-only pattern like "backup-mac-tese/"
        if pattern.endswith("/"):
            dir_pattern = pattern.rstrip("/")
            if is_dir and (
                rel_path.rstrip("/") == dir_pattern
                or rel_path.rstrip("/").startswith(dir_pattern + "/")
                or fnmatch.fnmatch(rel_path.rstrip("/"), dir_pattern)
            ):
                return True
            if rel_path.startswith(dir_pattern + "/") or fnmatch.fnmatch(rel_path, pattern):
                return True
            continue

        if (
            rel_path == pattern
            or fnmatch.fnmatch(rel_path, pattern)
            or fnmatch.fnmatch(Path(rel_path).name, pattern)
        ):
            return True

    return False


def should_skip(path: Path, project_root: Path, ignore_patterns: list[str], keep_patterns: list[str]) -> bool:
    rel_path = normalize_rel_path(path, project_root)
    is_dir = path.is_dir()

    # Keep rules have dominance
    if matches_pattern(rel_path, keep_patterns, is_dir):
        return False

    if matches_pattern(rel_path, ignore_patterns, is_dir):
        return True

    return False


def iter_tree_lines(
    current: Path,
    project_root: Path,
    ignore_patterns: list[str],
    keep_patterns: list[str],
    prefix: str = "",
) -> Iterable[str]:
    entries = [
        p
        for p in sorted(current.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        if not should_skip(p, project_root, ignore_patterns, keep_patterns)
    ]

    for index, entry in enumerate(entries):
        is_last = index == len(entries) - 1
        connector = "└── " if is_last else "├── "
        display_name = entry.name + ("/" if entry.is_dir() else "")
        yield f"{prefix}{connector}{display_name}"

        if entry.is_dir():
            extension = "    " if is_last else "│   "
            yield from iter_tree_lines(
                entry,
                project_root,
                ignore_patterns,
                keep_patterns,
                prefix + extension,
            )


def generate_structure_md(project_root: Path, ignore_patterns: list[str], keep_patterns: list[str]) -> None:
    lines: list[str] = [
        "# Project Structure",
        "",
        f"Root: `{project_root.name}/`",
        "",
        "```text",
        f"{project_root.name}/",
    ]

    lines.extend(iter_tree_lines(project_root, project_root, ignore_patterns, keep_patterns))
    lines.extend(["```", ""])

    (project_root / STRUCTURE_OUTPUT).write_text("\n".join(lines), encoding="utf-8")


def format_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    def fmt_arg(arg: ast.arg) -> str:
        if arg.annotation is not None:
            try:
                return f"{arg.arg}: {ast.unparse(arg.annotation)}"
            except Exception:
                return arg.arg
        return arg.arg

    parts: list[str] = []

    positional = list(node.args.posonlyargs) + list(node.args.args)
    defaults = list(node.args.defaults)
    default_start = len(positional) - len(defaults)

    for i, arg in enumerate(node.args.posonlyargs):
        item = fmt_arg(arg)
        if i >= default_start:
            try:
                item += f" = {ast.unparse(defaults[i - default_start])}"
            except Exception:
                item += " = ..."
        parts.append(item)

    if node.args.posonlyargs:
        parts.append("/")

    for i, arg in enumerate(node.args.args, start=len(node.args.posonlyargs)):
        item = fmt_arg(arg)
        if i >= default_start:
            try:
                item += f" = {ast.unparse(defaults[i - default_start])}"
            except Exception:
                item += " = ..."
        parts.append(item)

    if node.args.vararg is not None:
        parts.append(f"*{fmt_arg(node.args.vararg)}")
    elif node.args.kwonlyargs:
        parts.append("*")

    for kwarg, kwdefault in zip(node.args.kwonlyargs, node.args.kw_defaults):
        item = fmt_arg(kwarg)
        if kwdefault is not None:
            try:
                item += f" = {ast.unparse(kwdefault)}"
            except Exception:
                item += " = ..."
        parts.append(item)

    if node.args.kwarg is not None:
        parts.append(f"**{fmt_arg(node.args.kwarg)}")

    signature = f"{node.name}({', '.join(parts)})"

    if node.returns is not None:
        try:
            signature += f" -> {ast.unparse(node.returns)}"
        except Exception:
            pass

    return signature


def is_public(name: str) -> bool:
    return not name.startswith("_")


def get_top_level_functions(tree: ast.Module) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and is_public(node.name)
    ]


def get_methods(class_node: ast.ClassDef) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [
        node
        for node in class_node.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and is_public(node.name)
    ]


def parse_python_file(py_file: Path) -> dict:
    text = py_file.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(py_file))

    module_doc = ast.get_docstring(tree)
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef) and is_public(node.name)]
    functions = get_top_level_functions(tree)

    return {
        "module_doc": module_doc,
        "classes": classes,
        "functions": functions,
    }


def generate_api_docstrings_md(project_root: Path, ignore_patterns: list[str], keep_patterns: list[str]) -> None:
    py_files = [
        p
        for p in project_root.rglob("*.py")
        if not should_skip(p, project_root, ignore_patterns, keep_patterns)
        and not any(
            should_skip(parent, project_root, ignore_patterns, keep_patterns)
            for parent in p.parents
            if parent != project_root and project_root in parent.parents
        )
    ]
    py_files.sort(key=lambda p: str(p.relative_to(project_root)).lower())

    lines: list[str] = ["# API and Docstrings", ""]

    if not py_files:
        lines.append("_No Python files found._")
    else:
        for py_file in py_files:
            rel_path = py_file.relative_to(project_root)

            try:
                parsed = parse_python_file(py_file)
            except SyntaxError as exc:
                lines.extend([
                    f"## `{rel_path}`",
                    "",
                    f"**Error:** Could not parse file due to syntax error: `{exc}`",
                    "",
                    "---",
                    "",
                ])
                continue
            except Exception as exc:
                lines.extend([
                    f"## `{rel_path}`",
                    "",
                    f"**Error:** Failed to inspect file: `{exc}`",
                    "",
                    "---",
                    "",
                ])
                continue

            lines.extend([f"## `{rel_path}`", ""])

            module_doc = parsed["module_doc"]
            if module_doc:
                lines.extend([
                    "### Module Docstring",
                    "",
                    "```text",
                    module_doc,
                    "```",
                    "",
                ])

            functions = parsed["functions"]
            classes = parsed["classes"]

            if functions:
                lines.extend(["### Top-Level Functions", ""])
                for func in functions:
                    lines.extend([f"#### `{format_signature(func)}`", ""])
                    doc = ast.get_docstring(func)
                    if doc:
                        lines.extend(["```text", doc, "```", ""])
                    else:
                        lines.extend(["_No docstring._", ""])

            if classes:
                lines.extend(["### Classes", ""])
                for cls in classes:
                    lines.extend([f"#### `{cls.name}`", ""])
                    class_doc = ast.get_docstring(cls)
                    if class_doc:
                        lines.extend([
                            "**Class docstring**",
                            "",
                            "```text",
                            class_doc,
                            "```",
                            "",
                        ])
                    else:
                        lines.extend(["_No class docstring._", ""])

                    methods = get_methods(cls)
                    if methods:
                        lines.extend(["**Public methods**", ""])
                        for method in methods:
                            lines.append(f"- `{format_signature(method)}`")
                            method_doc = ast.get_docstring(method)
                            if method_doc:
                                lines.extend([
                                    "",
                                    "  ```text",
                                    *[f"  {line}" for line in method_doc.splitlines()],
                                    "  ```",
                                ])
                            else:
                                lines.append("  - _No docstring._")
                        lines.append("")

            if not module_doc and not functions and not classes:
                lines.extend(["_No public classes/functions or module docstring found._", ""])

            lines.extend(["---", ""])

    (project_root / API_OUTPUT).write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    project_root = Path.cwd()

    ignore_patterns = load_patterns(project_root / IGNORE_FILE)
    keep_patterns = load_patterns(project_root / KEEP_FILE)

    # Never include the generated outputs themselves unless explicitly kept.
    ignore_patterns = ignore_patterns + [STRUCTURE_OUTPUT, API_OUTPUT]

    generate_structure_md(project_root, ignore_patterns, keep_patterns)
    generate_api_docstrings_md(project_root, ignore_patterns, keep_patterns)

    print(f"Generated {STRUCTURE_OUTPUT} and {API_OUTPUT} in {project_root}")


if __name__ == "__main__":
    main()