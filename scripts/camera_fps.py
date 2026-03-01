# the goal of this script is to
# 1) measure the fps of different resolution modes of the camera

import cv2
import numpy as np
import yaml
from utils import get_project_root
from pathlib import Path
from camera import (
    CameraConfig,
    open_camera_by_index,
    open_configured_camera,
    test_resolution_mode_fps,
)
import time

ROOT = get_project_root(Path.cwd())
CONFIG = ROOT / "config" / "camera_config.yaml"
MODES = ROOT / "config" / "camera_resolution_modes.yaml"


def test_fps(cfg, modes, T=3, warmup_frames=5):
    cap = open_camera_by_index(cfg)
    fps_list = []
    for w, h in modes:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        print(f"testing mode {w}x{h}")
        for i in range(warmup_frames):
            ret, frame = cap.read()
        # check frame shape
        print(f"frame shape: {frame.shape[:2]}")
        t = time.perf_counter()
        n = 0
        while time.perf_counter() - t < T:
            ret, frame = cap.read()
            n = n+1
        fps = 1.0*n / (time.perf_counter()-t)
        fps_list.append(fps)
    return fps_list


def main():
    # read camera config
    with open(CONFIG, "r", encoding="utf-8") as f:
        cfg_dict = yaml.safe_load(f)
    cfg = CameraConfig(**cfg_dict)
    # read the different resolution modes
    with open(MODES, "r", encoding="utf-8") as f:
        modes_dict = yaml.safe_load(f)
    modes = modes_dict["modes"]
    # test fps of all modes
    for w, h in modes:
        cfg.wreq = w
        cfg.hreq = h
        cap = open_configured_camera(cfg)
        fps, dts = test_resolution_mode_fps(cap)
        print(f"mode {w}x{h}, fps {fps}Hz, mean dt {np.mean(dts)}, max dt {max(dts)}.")  
        cap.release()  

if __name__ == "__main__":
    main()