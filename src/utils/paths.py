import pathlib
from pathlib import Path

def get_project_root(start):
    if start is None:
        start = __file__

    current_path = Path(start).resolve()

    if current_path.is_file():
        current_path = current_path.parent

    for p in [current_path, *current_path.parents]:
        if (p / "pyproject.toml").exists():
            return p
    
    raise FileNotFoundError("Did not find the project root (pyproject.toml not found).")