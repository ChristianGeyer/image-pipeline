from pathlib import Path
from typing import Union


def get_project_root(start: Union[str, Path, None]) -> Path:
    """
    Locate the project root directory by searching for `pyproject.toml`.

    Starting from the given path (file or directory), this function walks up
    the directory tree until it finds a folder containing `pyproject.toml`.

    If no starting path is provided, the search begins from this file.

    Args:
        start: Starting path for the search.

    Returns:
        Absolute path to the project root directory.

    Raises:
        FileNotFoundError: If no parent directory contains `pyproject.toml`.
    """
    if start is None:
        start_path = Path(__file__).resolve()
    else:
        start_path = Path(start).resolve()

    if start_path.is_file():
        start_path = start_path.parent

    for p in (start_path, *start_path.parents):
        if (p / "pyproject.toml").exists():
            return p

    raise FileNotFoundError(
        "Did not find the project root (pyproject.toml not found)."
    )