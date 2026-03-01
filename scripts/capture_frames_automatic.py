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
        # extended capability for printing tis
        self.last_tis_printed = 0.0
        self.print_every_seconds = 0.5
    
    def update(self, new_state):
        if self.state != new_state:
            self.prev_state = self.state
            self.state = new_state
            self.tis = 0.0
            self.tes = time.perf_counter()
        else:
            self.tis = time.perf_counter()-self.tes
            self.prev_state = self.state

    def print_tis(self, tis_limit):
        if self.tis - self.last_tis_printed >= self.print_every_seconds:
            if tis_limit is None:
                print(f"tis = {self.tis}")
            else:
                print(f"tis = {self.tis}/{tis_limit}")
            self.last_tis_printed = self.tis

class State(Enum):
    VIDEO = auto()
    SET_PARAMS = auto()
    VIDEO_AUTO = auto()
    FREEZE = auto()

class InternalState:
    def __init__(self, N, T0, TF, TV):
        self.N = N 
        self.T0 = T0
        self.TF = TF
        self.TV = TV
        self.n = 0 # frames taken
        self.p = 0 # parameter being configured (N:0, T0:1, TF:2, TV:3)
        self.vals = [0, 0, 0, 0]

def print_internal_state(IS):
    if (IS.p < 0) or (IS.p > 3):
        return
    params = ["N", "T0", "TF", "TV"]
    print("setting ", params[IS.p])
    print(f"N = {IS.vals[0]}, T0 = {IS.vals[1]}, TF = {IS.vals[2]}, TV = {IS.vals[3]}")

def take_frame_and_display(cap, cfg):
    # take a frame and display it
    ret, frame = cap.read()
    frame = rotate_frame(frame, cfg)
    frame = flip_frame(frame, cfg)
    if cfg.rotation_deg in (90, 270):
        frame_display = cv2.resize(frame, (480, 640))
    else:
        frame_display = cv2.resize(frame, (640, 480))
    cv2.imshow("frame_display", frame_display)

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
    print("VIDEO")

    # create internal state object
    IS = InternalState(0, 0, 0, 0)

    while True:
        # read input keys
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break
        # state machine transitions
        if (fsm.state == State.VIDEO) and (k == SPACE):
            fsm.update(State.SET_PARAMS)
        elif (fsm.state == State.SET_PARAMS) and \
             ((k == SPACE) and (IS.p == 3)):
             fsm.update(State.VIDEO_AUTO)
        elif (fsm.state == State.VIDEO_AUTO) and \
             ((IS.n == 0) and (fsm.tis >= IS.T0) or (IS.n > 0) and (fsm.tis >= IS.TV)):
            fsm.update(State.FREEZE)
        elif (fsm.state == State.FREEZE) and \
            ((IS.n < IS.N) and (fsm.tis >= IS.TF)):
            fsm.update(State.VIDEO_AUTO)
        elif (fsm.state == State.FREEZE) and \
             ((IS.n == IS.N) and (fsm.tis >= IS.TF)):
             fsm.update(State.VIDEO)
        else:
            fsm.update(fsm.state)
        # state machine actions
        if fsm.state == State.VIDEO:
            if fsm.prev_state != fsm.state:
                print("VIDEO")
            # take a frame and display it
            take_frame_and_display(cap, cfg)
        elif fsm.state == State.SET_PARAMS:
            if fsm.state != fsm.prev_state:
                print("SET_PARAMS")
            # reset p when entering the state
            if fsm.prev_state != fsm.state:
                IS.p = 0
                IS.vals = [1, 1, 1, 1]
                print_internal_state(IS)
            # on k == d, increment parameter val
            if k == ord('d'):
                IS.vals[IS.p] += 1
                print_internal_state(IS)
            # on k == a, decrement parameter val
            elif k == ord('a'):
                IS.vals[IS.p] -= 1
                if IS.vals[IS.p] < 0:
                    IS.vals[IS.p] = 0
                print_internal_state(IS)
            # on SPACE, increment p
            elif (k == SPACE) and (fsm.prev_state == fsm.state):
                IS.p += 1
                print_internal_state(IS)
            # take a frame and display it
            take_frame_and_display(cap, cfg)
        elif fsm.state == State.VIDEO_AUTO:
            if fsm.prev_state != fsm.state:
                print("VIDEO_AUTO")
            # reset n when entering the state from the set params state
            if fsm.prev_state == State.SET_PARAMS:
                IS.n = 0
            # set the internal state with the param vals when coming from the set params state
            if fsm.prev_state == State.SET_PARAMS:
                IS.N, IS.T0, IS.TF, IS.TV = IS.vals
            # take frame and display
            take_frame_and_display(cap, cfg)
            # print tis
            if IS.n == 0:
                fsm.print_tis(IS.T0)
            else:
                fsm.print_tis(IS.TV)
        elif fsm.state == State.FREEZE:
            if fsm.prev_state != fsm.state:
                print("FREEZE")
            # increment n when entering
            if fsm.prev_state != fsm.state:
                IS.n += 1
            # take a frame and display it if entering this state
            if fsm.prev_state != fsm.state:
                # take a frame and display it
                take_frame_and_display(cap, cfg)
            # print tis
            fsm.print_tis(IS.TF)
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()