from pathlib import Path

def get_root_dir(current_path):
    # get current file path
    for p in (current_path, *current_path.parents):
        if (p / "pyproject.toml").exists():
            return p
    raise FileNotFoundError("Could not find root of the project, no pyproject.toml found.")