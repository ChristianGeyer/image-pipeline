import cv2
import numpy as np
import yaml
import time
from utils import get_project_root
from pathlib import Path
from camera import (
    CameraConfig,
    open_camera_by_index,
    rotate_frame, 
    flip_frame,
)

ROOT = get_project_root(Path.cwd())
CONFIG = ROOT / "config" / "camera_config.yaml" 

def downsampled_dimensions(cfg, downsample_factor):
    w_downsampled = int(cfg.wreq // downsample_factor)
    h_downsampled = int(cfg.hreq // downsample_factor)
    if cfg.rotation_deg in (90, 270):
        return h_downsampled, w_downsampled
    return w_downsampled, h_downsampled

def main():
    # load camera_config dictionary
    with open(CONFIG, "r", encoding="utf-8") as f:
        cfg_dict = yaml.safe_load(f)
    # create camera config object
    cfg = CameraConfig(**cfg_dict)
    # open camera
    cap = open_camera_by_index(cfg)
    # set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.wreq)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.hreq)
    # display downsample
    downsample_factor = 4
    # downsampled dimensions
    w_display, h_display = downsampled_dimensions(cfg, downsample_factor)
    print(f"downsampled to {w_display}x{h_display}.")

    ret, frame = cap.read()
    print(f"frame shape: {frame.shape[1]}x{frame.shape[0]}, expected shape: {cfg.wreq}x{cfg.hreq}.")

    # fps measurement
    t = time.perf_counter()
    t1 = t
    T = 10 # seconds
    n = 0 # frame count
    dts = [] # loop times
    while True:
        # read frame
        ret, frame = cap.read()
        n = n+1
        # rotate frame
        frame = rotate_frame(frame, cfg)
        # flip frame
        frame = flip_frame(frame, cfg)
        # downsample frame
        frame_display = cv2.resize(frame, (w_display, h_display))
        # display frame
        cv2.imshow("frame_display", frame_display)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        # fps measurement and logging
        dt = time.perf_counter()-t1
        t1 = time.perf_counter()
        dts.append(dt)
        if (t1-t) > T:
            fps = n / (t1-t)
            print(f"fps {fps}Hz, max dt {max(dts)}, mean dt {np.mean(dts)}.")
            t = t1
            n = 0
            dts = []
    
    cap.release()
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()