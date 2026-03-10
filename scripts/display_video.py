# python libraries
import cv2
import numpy as np
import yaml
import time
from pathlib import Path

# my library
from utils import (
    get_project_root,
    RateMonitor,
)
from camera import (
    CameraConfig,
    open_configured_camera,
    rotate_frame, 
    flip_frame,
)

# paths
ROOT = get_project_root(Path.cwd())
CONFIG = ROOT / "config" / "camera_config.yaml" 

class DisplayFrame:
    def __init__(self,
                 cap, 
                 cfg, 
                 display_size):
        self.cap = cap
        self.cfg = cfg
        self.display_size = display_size # (w, h)

def get_display_frame(frame, df):
    cap = df.cap
    cfg = df.cfg
    w_display, h_display = df.display_size
    # read frame
    ret, frame = cap.read()
    # rotate frame
    frame = rotate_frame(frame, cfg)
    # flip frame
    frame = flip_frame(frame, cfg)
    # resize frame
    frame_display = cv2.resize(frame, (w_display, h_display))
    # display frame
    return frame_display

def main():
    # load camera_config dictionary
    with open(CONFIG, "r", encoding="utf-8") as f:
        cfg_dict = yaml.safe_load(f)
    # create camera config object
    cfg = CameraConfig(**cfg_dict)
    # open camera
    cap, wframes = open_configured_camera(cfg)
    h, w = wframes[0].shape[:2]
    # display dimensions
    w_display = 480
    if cfg.rotation_deg in (90, 270):
        h_display = int(w_display * w / h)
    else:
        h_display = int(w_display * h / w)

    print(f"display frame resolution: {w_display}x{h_display}.")

    # display frame object
    df = DisplayFrame(cap, cfg, (w_display, h_display))

    # rate monitor
    T = 3
    rate_monitor = RateMonitor(T)
    rate_monitor.reset(time.perf_counter())

    while True:
        # read key
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break
        # read frame
        ret, frame = cap.read()
        if not ret:
            raise RuntimeError("could not read frame.")
        # get display frame
        display_frame = get_display_frame(frame, df)
        # display frame
        cv2.imshow("frame_display", display_frame)

        # rate monitor
        rate_monitor.increment(time.perf_counter())

    cap.release()
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()