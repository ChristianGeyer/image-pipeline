"""
Generate project documentation files from source code and project metadata.

This module provides reusable functions to generate:
- PROJECT_TREE.md
- API_DOCSTRINGS.md

Generation rules:
- API_DOCSTRINGS.md includes PROJECT_SPECIFICATION.md at the beginning
- API_DOCSTRINGS.md scans only Python files under `src/` and `scripts/`
- PROJECT_TREE.md includes the full project tree, excluding paths ignored by
  `.gitignore`

The generated API documentation includes:
- module docstrings
- public top-level functions
- public classes
- public properties
- public methods

Public means:
- top-level names not starting with `_`
- class member names not starting with `_`
"""

from __future__ import annotations

import ast
import fnmatch
from collections.abc import Iterable
from pathlib import Path

from utils import get_project_root


TREE_OUTPUT_NAME = "PROJECT_TREE.md"
API_OUTPUT_NAME = "API_DOCSTRINGS.md"
SPECIFICATION_NAME = "PROJECT_SPECIFICATION.md"
GITIGNORE_NAME = ".gitignore"
API_SCAN_DIRS = ("src", "scripts")


def load_gitignore_patterns(file_path: Path) -> list[str]:
    """
    Load non-empty, non-comment patterns from `.gitignore`.

    Args:
        file_path: Path to `.gitignore`.

    Returns:
        List of pattern strings. Returns an empty list if the file does not
        exist.
    """
    if not file_path.exists():
        return []

    patterns: list[str] = []
    for line in file_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            patterns.append(stripped)
    return patterns


def normalize_rel_path(path: Path, project_root: Path) -> str:
    """
    Return a project-relative path using POSIX separators.

    Directory paths end with `/`.

    Args:
        path: File or directory path inside the project.
        project_root: Project root directory.

    Returns:
        Relative path from `project_root` to `path`, with `/` separators.
    """
    rel = path.relative_to(project_root).as_posix()
    return f"{rel}/" if path.is_dir() else rel


def gitignore_match(rel_path: str, pattern: str, is_dir: bool) -> bool:
    """
    Return whether a project-relative path matches one `.gitignore` pattern.

    Supported behavior:
    - comments and blank lines are ignored by the caller
    - trailing `/` means directory-only pattern
    - leading `/` anchors the pattern at project root
    - patterns without `/` match by basename at any depth
    - patterns with `/` match against the full relative path
    - simple glob matching uses `fnmatch`

    Negation patterns (`!pattern`) are not supported.

    Args:
        rel_path: Project-relative POSIX path. Directories end with `/`.
        pattern: One `.gitignore` pattern.
        is_dir: Whether `rel_path` refers to a directory.

    Returns:
        True if the pattern matches, otherwise False.
    """
    if not pattern or pattern.startswith("!"):
        return False

    directory_only = pattern.endswith("/")
    if directory_only:
        pattern = pattern[:-1]

    anchored = pattern.startswith("/")
    if anchored:
        pattern = pattern[1:]

    target = rel_path[:-1] if rel_path.endswith("/") else rel_path
    name = Path(target).name

    if directory_only and not is_dir:
        return False

    if anchored:
        if fnmatch.fnmatch(target, pattern):
            return True
        if is_dir and (target == pattern or target.startswith(f"{pattern}/")):
            return True
        return False

    if "/" in pattern:
        if fnmatch.fnmatch(target, pattern):
            return True
        if is_dir and (target == pattern or target.startswith(f"{pattern}/")):
            return True
        return False

    if fnmatch.fnmatch(name, pattern):
        return True
    if fnmatch.fnmatch(target, pattern):
        return True
    if is_dir and (target == pattern or target.startswith(f"{pattern}/")):
        return True

    return False


def is_gitignored(path: Path, project_root: Path, patterns: list[str]) -> bool:
    """
    Return whether a project path should be excluded from PROJECT_TREE.md.

    Exclusion rules:
    - `.git/` is always excluded
    - `.gitignore` patterns are applied in file order
    - only ignore patterns are supported; negation patterns are ignored

    Args:
        path: Candidate path.
        project_root: Project root directory.
        patterns: Patterns loaded from `.gitignore`.

    Returns:
        True if the path should be excluded, otherwise False.
    """
    rel_path = normalize_rel_path(path, project_root)

    if rel_path == ".git/" or rel_path.startswith(".git/"):
        return True

    ignored = False
    for pattern in patterns:
        if pattern.startswith("!"):
            continue
        if gitignore_match(rel_path, pattern, path.is_dir()):
            ignored = True

    return ignored


def iter_tree_lines(
    current: Path,
    project_root: Path,
    gitignore_patterns: list[str],
    prefix: str = "",
) -> Iterable[str]:
    """
    Yield formatted tree lines for a project subtree.

    Traversal behavior:
    - paths ignored by `.gitignore` are omitted
    - `.git/` is omitted
    - children are sorted with directories first, then files
    - names are emitted using tree connectors

    Args:
        current: Current directory to traverse.
        project_root: Project root directory.
        gitignore_patterns: Patterns loaded from `.gitignore`.
        prefix: Prefix used for nested tree indentation.

    Yields:
        One formatted tree line per included path.
    """
    children = [
        child
        for child in sorted(current.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        if not is_gitignored(child, project_root, gitignore_patterns)
    ]

    for index, child in enumerate(children):
        is_last = index == len(children) - 1
        connector = "└── " if is_last else "├── "
        display_name = f"{child.name}/" if child.is_dir() else child.name
        yield f"{prefix}{connector}{display_name}"

        if child.is_dir():
            extension = "    " if is_last else "│   "
            yield from iter_tree_lines(
                current=child,
                project_root=project_root,
                gitignore_patterns=gitignore_patterns,
                prefix=prefix + extension,
            )


def generate_project_tree_md(project_root: Path | None = None) -> Path:
    """
    Generate PROJECT_TREE.md at the project root.

    The output contains the full project directory tree after excluding paths
    matched by `.gitignore`.

    Args:
        project_root: Project root directory. If None, it is resolved
            automatically.

    Returns:
        Path to the generated PROJECT_TREE.md file.
    """
    resolved_root = get_project_root(project_root)
    gitignore_patterns = load_gitignore_patterns(resolved_root / GITIGNORE_NAME)

    lines = [
        "# Project Tree",
        "",
        "```text",
        f"{resolved_root.name}/",
        *iter_tree_lines(
            current=resolved_root,
            project_root=resolved_root,
            gitignore_patterns=gitignore_patterns,
        ),
        "```",
        "",
    ]

    output_path = resolved_root / TREE_OUTPUT_NAME
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def format_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """
    Return a compact source-like signature for a function node.

    Behavior:
    - includes positional, vararg, keyword-only, and kwarg parameters
    - includes defaults when available
    - includes return annotation when available
    - does not include decorators or function body

    Args:
        node: Function AST node.

    Returns:
        Signature string such as `f(x: int, y=1) -> str`.
    """
    args = node.args
    parts: list[str] = []

    positional = list(args.posonlyargs) + list(args.args)
    positional_defaults = [None] * (len(positional) - len(args.defaults)) + list(args.defaults)

    for index, (arg, default) in enumerate(zip(positional, positional_defaults)):
        text = arg.arg
        if arg.annotation is not None:
            text += f": {ast.unparse(arg.annotation)}"
        if default is not None:
            text += f" = {ast.unparse(default)}"
        parts.append(text)

        if args.posonlyargs and index == len(args.posonlyargs) - 1:
            parts.append("/")

    if args.vararg is not None:
        text = f"*{args.vararg.arg}"
        if args.vararg.annotation is not None:
            text += f": {ast.unparse(args.vararg.annotation)}"
        parts.append(text)
    elif args.kwonlyargs:
        parts.append("*")

    for kwarg, default in zip(args.kwonlyargs, args.kw_defaults):
        text = kwarg.arg
        if kwarg.annotation is not None:
            text += f": {ast.unparse(kwarg.annotation)}"
        if default is not None:
            text += f" = {ast.unparse(default)}"
        parts.append(text)

    if args.kwarg is not None:
        text = f"**{args.kwarg.arg}"
        if args.kwarg.annotation is not None:
            text += f": {ast.unparse(args.kwarg.annotation)}"
        parts.append(text)

    signature = f"{node.name}({', '.join(parts)})"
    if node.returns is not None:
        signature += f" -> {ast.unparse(node.returns)}"
    return signature


def format_property_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """
    Return a compact source-like signature for a property getter.

    Args:
        node: Property getter AST node.

    Returns:
        Signature string such as `state -> Any`.
    """
    signature = node.name
    if node.returns is not None:
        signature += f" -> {ast.unparse(node.returns)}"
    return signature


def is_public(name: str) -> bool:
    """
    Return whether a name is public by project-doc conventions.

    Args:
        name: Candidate symbol name.

    Returns:
        True if the name does not start with `_`, otherwise False.
    """
    return not name.startswith("_")


def is_property_getter(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """
    Return whether a function node is decorated with `@property`.

    Args:
        node: Function AST node.

    Returns:
        True if the node is a property getter, otherwise False.
    """
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Name) and decorator.id == "property":
            return True
    return False


def is_property_setter(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """
    Return whether a function node is decorated with `@<name>.setter`.

    Args:
        node: Function AST node.

    Returns:
        True if the node is a property setter, otherwise False.
    """
    for decorator in node.decorator_list:
        if (
            isinstance(decorator, ast.Attribute)
            and decorator.attr == "setter"
            and isinstance(decorator.value, ast.Name)
        ):
            return True
    return False


def is_property_deleter(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """
    Return whether a function node is decorated with `@<name>.deleter`.

    Args:
        node: Function AST node.

    Returns:
        True if the node is a property deleter, otherwise False.
    """
    for decorator in node.decorator_list:
        if (
            isinstance(decorator, ast.Attribute)
            and decorator.attr == "deleter"
            and isinstance(decorator.value, ast.Name)
        ):
            return True
    return False


def get_top_level_functions(tree: ast.Module) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    """
    Return public top-level function definitions from a module AST.

    Args:
        tree: Parsed module AST.

    Returns:
        Public top-level function nodes in source order.
    """
    return [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and is_public(node.name)
    ]


def get_classes(tree: ast.Module) -> list[ast.ClassDef]:
    """
    Return public top-level class definitions from a module AST.

    Args:
        tree: Parsed module AST.

    Returns:
        Public class nodes in source order.
    """
    return [
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and is_public(node.name)
    ]


def get_properties(class_node: ast.ClassDef) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    """
    Return public property getters declared directly on a class.

    Only `@property` getters are included. Setters and deleters are excluded
    from the generated API method list.

    Args:
        class_node: Class AST node.

    Returns:
        Public property getter nodes in source order.
    """
    return [
        node
        for node in class_node.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and is_public(node.name)
        and is_property_getter(node)
    ]


def get_methods(class_node: ast.ClassDef) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    """
    Return public non-property methods declared directly on a class.

    Excluded members:
    - `@property` getters
    - `@<name>.setter`
    - `@<name>.deleter`

    Args:
        class_node: Class AST node.

    Returns:
        Public non-property method nodes in source order.
    """
    return [
        node
        for node in class_node.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and is_public(node.name)
        and not is_property_getter(node)
        and not is_property_setter(node)
        and not is_property_deleter(node)
    ]


def extract_module_docstring(tree: ast.Module) -> str | None:
    """
    Return the cleaned module docstring from a parsed module.

    Args:
        tree: Parsed module AST.

    Returns:
        Module docstring, or None if absent.
    """
    return ast.get_docstring(tree, clean=True)


def parse_python_file(py_file: Path, project_root: Path) -> dict:
    """
    Parse a Python file into documentation-oriented metadata.

    Extracted data:
    - relative path
    - module docstring
    - public top-level functions with signatures/docstrings
    - public classes with docstrings, public properties, and public methods

    Args:
        py_file: Python file to parse.
        project_root: Project root directory.

    Returns:
        Dictionary containing parsed documentation data.
    """
    source = py_file.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(py_file))

    functions = []
    for node in get_top_level_functions(tree):
        functions.append(
            {
                "name": node.name,
                "signature": format_signature(node),
                "docstring": ast.get_docstring(node, clean=True),
            }
        )

    classes = []
    for class_node in get_classes(tree):
        properties = []
        for prop in get_properties(class_node):
            properties.append(
                {
                    "name": prop.name,
                    "signature": format_property_signature(prop),
                    "docstring": ast.get_docstring(prop, clean=True),
                }
            )

        methods = []
        for method in get_methods(class_node):
            methods.append(
                {
                    "name": method.name,
                    "signature": format_signature(method),
                    "docstring": ast.get_docstring(method, clean=True),
                }
            )

        classes.append(
            {
                "name": class_node.name,
                "docstring": ast.get_docstring(class_node, clean=True),
                "properties": properties,
                "methods": methods,
            }
        )

    return {
        "path": normalize_rel_path(py_file, project_root),
        "module_docstring": extract_module_docstring(tree),
        "functions": functions,
        "classes": classes,
    }


def iter_api_python_files(project_root: Path) -> Iterable[Path]:
    """
    Yield Python files to include in API_DOCSTRINGS.md.

    Included files:
    - all `.py` files under `src/`
    - all `.py` files under `scripts/`

    Excluded files:
    - files outside those two directories

    Args:
        project_root: Project root directory.

    Yields:
        Python file paths in deterministic order.
    """
    files: list[Path] = []

    for dirname in API_SCAN_DIRS:
        root = project_root / dirname
        if not root.exists() or not root.is_dir():
            continue
        files.extend(path for path in root.rglob("*.py") if path.is_file())

    for path in sorted(set(files), key=lambda p: p.relative_to(project_root).as_posix().lower()):
        yield path


def render_docstring_block(docstring: str) -> list[str]:
    """
    Render a docstring as a fenced text block.

    Args:
        docstring: Cleaned docstring text.

    Returns:
        Markdown lines representing the docstring.
    """
    return [
        "```text",
        docstring,
        "```",
    ]


def render_indented_docstring_block(docstring: str, indent: str = "  ") -> list[str]:
    """
    Render a docstring as an indented fenced text block.

    Args:
        docstring: Cleaned docstring text.
        indent: Prefix added to each rendered line.

    Returns:
        Markdown lines representing the indented docstring block.
    """
    lines = [f"{indent}```text"]
    lines.extend(f"{indent}{line}" for line in docstring.splitlines())
    lines.append(f"{indent}```")
    return lines


def render_module_section(parsed: dict) -> list[str]:
    """
    Render one module section for API_DOCSTRINGS.md.

    Rendering behavior:
    - includes module heading
    - includes module docstring if present
    - includes public top-level functions
    - includes public classes, public properties, and public methods
    - emits fallback text when no public API/docstring is present

    Args:
        parsed: Parsed module metadata.

    Returns:
        Markdown lines for the module section.
    """
    lines = [f"## `{parsed['path']}`", ""]

    has_module_docstring = parsed["module_docstring"] is not None
    has_functions = bool(parsed["functions"])
    has_classes = bool(parsed["classes"])

    if has_module_docstring:
        lines.extend(["### Module Docstring", ""])
        lines.extend(render_docstring_block(parsed["module_docstring"]))
        lines.append("")

    if has_functions:
        lines.extend(["### Top-Level Functions", ""])
        for function in parsed["functions"]:
            lines.append(f"#### `{function['signature']}`")
            lines.append("")
            if function["docstring"]:
                lines.extend(render_docstring_block(function["docstring"]))
            else:
                lines.append("_No docstring._")
            lines.append("")

    if has_classes:
        lines.extend(["### Classes", ""])
        for cls in parsed["classes"]:
            lines.append(f"#### `{cls['name']}`")
            lines.append("")

            if cls["docstring"]:
                lines.extend(["**Class docstring**", ""])
                lines.extend(render_docstring_block(cls["docstring"]))
                lines.append("")
            else:
                lines.append("_No class docstring._")
                lines.append("")

            if cls["properties"]:
                lines.extend(["**Public properties**", ""])
                for prop in cls["properties"]:
                    lines.append(f"- `{prop['signature']}`")
                    lines.append("")
                    if prop["docstring"]:
                        lines.extend(render_indented_docstring_block(prop["docstring"]))
                    else:
                        lines.append("  _No docstring._")
                lines.append("")

            if cls["methods"]:
                lines.extend(["**Public methods**", ""])
                for method in cls["methods"]:
                    lines.append(f"- `{method['signature']}`")
                    lines.append("")
                    if method["docstring"]:
                        lines.extend(render_indented_docstring_block(method["docstring"]))
                    else:
                        lines.append("  _No docstring._")
                lines.append("")

    if not has_module_docstring and not has_functions and not has_classes:
        lines.append("_No public classes/functions or module docstring found._")
        lines.append("")

    lines.extend(["---", ""])
    return lines


def read_project_specification(project_root: Path) -> str:
    """
    Read PROJECT_SPECIFICATION.md from the project root.

    Args:
        project_root: Project root directory.

    Returns:
        Full specification file contents.

    Raises:
        FileNotFoundError: If PROJECT_SPECIFICATION.md does not exist.
    """
    spec_path = project_root / SPECIFICATION_NAME
    return spec_path.read_text(encoding="utf-8").rstrip()


def generate_api_docstrings_md(project_root: Path | None = None) -> Path:
    """
    Generate API_DOCSTRINGS.md at the project root.

    Output structure:
    - PROJECT_SPECIFICATION.md contents
    - `# API and Docstrings`
    - one section per included Python module

    Included modules:
    - all `.py` files under `src/`
    - all `.py` files under `scripts/`

    Args:
        project_root: Project root directory. If None, it is resolved
            automatically.

    Returns:
        Path to the generated API_DOCSTRINGS.md file.
    """
    resolved_root = get_project_root(project_root)

    lines: list[str] = [
        read_project_specification(resolved_root),
        "",
        "# API and Docstrings",
        "",
    ]

    py_files = list(iter_api_python_files(resolved_root))
    if not py_files:
        lines.append("_No Python files found under `src/` or `scripts/`._")
        lines.append("")
    else:
        for py_file in py_files:
            parsed = parse_python_file(py_file, resolved_root)
            lines.extend(render_module_section(parsed))

    output_path = resolved_root / API_OUTPUT_NAME
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path