import pathlib
from pathlib import Path
import time

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

"""
Dataset Folder Structure:

Dataset/
    Session_000001_20260304/
    Session_000002_20260304/
    Session_000001_20260305/
        E_000001_20260305_113341/
        E_000002_20260305_114345/
            img_000001_20260305_114345_212.png
        I_000001_20260305_113045/
        I_000002_20260305_114003/

"""

class FolderInfo:
    def __init__(self,
                 folder_type,
                 folder_id):
        if folder_type not in ["I", "E", "T"]:
            raise ValueError(f"folder_type {folder_type} should be one of [I, E, T].")
        self.folder_type = folder_type
        self.folder_id = folder_id
    
    def __repr__(self):
        return folder_type + f"{folder_id:06d}"

    def name_with_date(timestamp=None):
        # get current timestamp if None is passed
        if timestamp is None:
            timestamp = time.time()
        # convert timestamp to YYMMDD_HHMMSS:
        date = time.strftime("%y%m%d_%H%M%S", timestamp)
        return str(self) + "_" + date


class FileInfo:
    def __init__(self,
                 file_type,
                 file_id):
        self.file_type = file_type
        self.file_id = file_id

# save file to folder
def save_file_to_folder(fileinfo, folderinfo):
    pass
    

# follow a deterministic folder structure in the datasets folder:
# dataset/
#   session_<date>/
#       I_<id>_<timestamp>/
#       E_<id>_<timestamp>/
#       T_<id>_<timestamp>/
def create_raw_data_folder(dataset_path, folder_type, id):
    # check if dataset folder exists
    folder = Path(dataset_path)
    if not folder.exists():
        raise FileNotFoundError(f"dataset folder {dataset_path} does not exist.")
    # check folder_type
    if folder_type not in ["I", "E", "T"]:
        raise ValueError(f"folder_type {folder_type} not in [I, E, T].")
    # get the date and timestamp
    localtime = time.localtime()
    timestamp_days = time.strftime("%Y%m%d", localtime)
    timestamp_seconds = time.strftime("%Y%m%d_%H%M%S%", localtime)
    # session folder
    session_folder = folder / f"session_{timestamp_days}"
    # raw data folder
    id = 0
    raw_data_folder = session_folder / f"{folder_type}_{id:06d}" 

