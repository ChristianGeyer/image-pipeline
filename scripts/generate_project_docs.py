"""
Generate project documentation files at the project root.

Generated files:
- PROJECT_TREE.md
- API_DOCSTRINGS.md

Run from the project root:
    python scripts/generate_project_docs.py
"""

from project_docs import generate_api_docstrings_md, generate_project_tree_md


def main() -> None:
    """
    Generate PROJECT_TREE.md and API_DOCSTRINGS.md.

    Generation order:
    1. PROJECT_TREE.md
    2. API_DOCSTRINGS.md
    """
    generate_project_tree_md()
    generate_api_docstrings_md()


if __name__ == "__main__":
    main()