# the goal of this script is to
# 1) print all the resolution modes of the camera
# 2) test the fps when reading frames with each resolution

import cv2
import numpy as np
import yaml
from utils import get_project_root
from pathlib import Path
from camera import (
    CameraConfig,
    open_camera_by_index,
    test_resolution_modes,
)

ROOT = get_project_root(Path.cwd())
CONFIG = ROOT / "config" / "camera_config.yaml"
MODES = ROOT / "config" / "camera_resolution_modes.yaml"

def main():
    # read camera config
    with open(CONFIG, "r", encoding="utf-8") as f:
        cfg_dict = yaml.safe_load(f)
    cfg = CameraConfig(**cfg_dict)
    print(f"cfg_dict = {cfg_dict}") 
    # test resolution modes
    distinct, complete = test_resolution_modes(cfg, 1, 8, 50)
    print("complete:")
    for w1, h1, w2, h2 in complete:
        print(f"requested {w1}x{h1} got {w2}x{h2}.")
    print("distinct:")
    for w, h in distinct:
        print(f"{w}x{h}")
    yaml_dict = {}
    yaml_dict["modes"] = distinct
    with open(MODES, "w", encoding="utf-8") as f:
        yaml.safe_dump(yaml_dict, f, sort_keys=False)

if __name__ == "__main__":
    main()