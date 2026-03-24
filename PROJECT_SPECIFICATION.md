# Project Specification

This file defines the project-wide rules for code generation and documentation.

Its purpose is to make the codebase reproducible from generated documentation alone, so that future development can be done without direct access to the source code.

## Public API Rule

Use only public package APIs exposed through package `__init__.py` files.

Examples:
- Import from `camera`, not from `camera.camera`
- Import from `utils`, not from `utils.paths` or `utils.fsm`

Internal submodules may be used only when explicitly required.

## Documentation Rule

Every public module, class, and function must include a docstring.

Docstrings must be written so that a developer or LLM can correctly use and reimplement the code without reading the implementation.

## Deterministic Docstring Rule

Docstrings must be complete and deterministic.

This means:
- Fully specify behavior, not just intent
- Do not omit important steps, conditions, or state handling
- Avoid leaving implementation choices open when they affect behavior
- If multiple behaviors are possible, the docstring must make one explicit

Two independent implementations based only on the API documentation should produce equivalent behavior.

## Compactness Rule

Docstrings must be as compact as possible while remaining complete.

This means:
- Avoid unnecessary prose, repetition, or tutorial-style explanation
- Prefer structured, high-information formats
- Include only information required to determine behavior and usage

## Required Public Docstring Content

When applicable, public docstrings should include:

- purpose
- exact behavior
- arguments
- return values
- raised exceptions
- side effects
- state transitions, for stateful logic
- filesystem effects, if files or directories are created, modified, or removed

## API Stability Rule

Package `__init__.py` files define the intended public API surface.

Anything re-exported there is public.
Anything only available in internal submodules should be treated as internal unless explicitly documented otherwise.

## Code Generation Rule

When generating new code or modifying existing code:

- preserve the existing public API style
- preserve naming conventions
- preserve the documented behavior
- do not introduce alternative abstractions or redesigns unless explicitly required
- prefer simple, direct implementations that match the documented behavior closely

## Generated Documentation Rule

Generated project documentation should be sufficient for future code generation without requiring access to the full source code.

At minimum, generated documentation should include:
- the project tree
- the public API signatures
- all public docstrings
- module docstrings for package entry points such as `camera` and `utils`

## Script and Module Design Rule

If a script’s logic is reusable, prefer implementing it in functions and having the script only call those functions.

Scripts should stay thin when possible.

## Naming Rule

Use names that distinguish:
- hand-written specification files
- generated documentation files
- generator scripts
- reusable generator modules