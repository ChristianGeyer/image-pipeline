import cv2
import numpy as np
import time
from enum import Enum, auto
from utils import get_project_root
from pathlib import Path
import yaml
from camera import *

ROOT = get_project_root(Path.cwd())
CONFIG = ROOT / "config" / "camera_config.yaml"

SPACE = 32

class FSM:
    def __init__(self,
                 state):
        self.state = state
        self.prev_state = None
        self.tis = 0.0
        self.tes = 0.0
    
    def update(self, new_state):
        if self.state != new_state:
            self.prev_state = self.state
            self.state = new_state
            self.tis = 0.0
            self.tes = time.perf_counter()
        else:
            self.tis = time.perf_counter()-self.tes
            self.prev_state = self.state

class State(Enum):
    VIDEO = auto()
    FREEZE = auto()

def main():
    # load camera config yaml
    with open(CONFIG, "r", encoding="utf-8") as f:
        cfg_dict = yaml.safe_load(f)
    # create camera config object
    cfg = CameraConfig(**cfg_dict)
    # open camera
    cap = open_configured_camera(cfg)

    # state machine to go between video and freeze
    fsm = FSM(State.VIDEO)

    while True:
        # read input keys
        k = cv2.waitKey(1) & 0xFF
        # state machine transitions
        if (fsm.state == State.VIDEO) and (k == SPACE):
            fsm.update(State.FREEZE)
        elif (fsm.state == State.FREEZE) and (fsm.tis > 1):
            fsm.update(State.VIDEO)
        else:
            fsm.update(fsm.state)
        # state machine actions
        if fsm.state == State.VIDEO:
            # take a frame and display it
            ret, frame = cap.read()
            frame = rotate_frame(frame, cfg)
            frame = flip_frame(frame, cfg)
            if cfg.rotation_deg in (90, 270):
                frame_display = cv2.resize(frame, (480, 640))
            else:
                frame_display = cv2.resize(frame, (640, 480))
            cv2.imshow("frame_display", frame_display)
        elif fsm.state == State.FREEZE:
            # take a frame and display it if entering this state
            if fsm.prev_state != fsm.state:
                # take a frame and display it
                ret, frame = cap.read()
                frame = rotate_frame(frame, cfg)
                frame = flip_frame(frame, cfg)
                if cfg.rotation_deg in (90, 270):
                    frame_display = cv2.resize(frame, (480, 640))
                else:
                    frame_display = cv2.resize(frame, (640, 480))
                
                cv2.imshow("frame_display", frame_display)


if __name__ == "__main__":
    main()