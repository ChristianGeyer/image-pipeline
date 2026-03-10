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
DATASET = ROOT / ".." / "Datasets" / "image-pipeline"

SPACE = 32

class FSM:
    def __init__(self,
                 state):
        self.state = state
        self.prev_state = None
        self.tis = 0.0
        self.tes = 0.0
        # extended capability for printing tis
        self.last_print_time = 0.0
        self.time_between_prints = 0.5

    def __str__(self):
        prev_state_str = state2string(self.prev_state)
        state_str = state2string(self.state)
        return "prev:" + prev_state_str + " curr:" + state_str + " tis:" + f"{self.tis}"
    
    def update(self, new_state):
        if self.state != new_state:
            self.prev_state = self.state
            self.state = new_state
            self.tis = 0.0
            self.tes = time.perf_counter()
        else:
            self.tis = time.perf_counter()-self.tes
            self.prev_state = self.state

    def should_print(self):
        if self.tis - self.last_print_time >= self.time_between_prints:
            return True
        elif self.prev_state != self.state:
            return True
        return False

    def update_after_print(self):
        self.last_print_time = self.tis

class State(Enum):
    SETUP = auto()
    VIDEO = auto()
    FREEZE = auto()
    PARAMS = auto()
    VIDEO_AUTO = auto()
    FREEZE_AUTO = auto()
    UNKNOWN = auto()

def state2string(s):
    if s == State.SETUP:
        return "SETUP"
    elif s == State.VIDEO:
        return "VIDEO"
    elif s == State.FREEZE:
        return "FREEZE"
    elif s == State.PARAMS:
        return "PARAMS"
    elif s == State.VIDEO_AUTO:
        return "VIDEO_AUTO"
    elif s == State.FREEZE_AUTO:
        return "FREEZE_AUTO"
    return "UNKNOWN"

class InternalState:
    def __init__(self):
        # global internal state
        self.Types = ["I", "E", "T"] # intrinsics, extrinsics, targets
        self.t = 0 # type index to access Types
        self.id = 0
        self.n = 0 #  global frame count
        self.psetup = 0 # setup pointer (0->type, 1->id, 2->TVM)
        # manual mode internal state
        self.TFM = 1
        # automatic mode internal state
        self.dn = 0 # automatic mode frame count
        self.N = 1
        self.T0 = 1
        self.TFA = 1
        self.TVA = 1
        self.p = 0 # parameter pointer (0->N, 1->T0, 2->TFA, 3->TVA)
        self.vals = [0, 0, 0, 0] # parameter vals in a list
        # to detect changes
        self.changed = False

def print_internal_state(IS):
    print(f"Type:{IS.Types[IS.t]}, id:{IS.id}, n:{IS.n}, psetup:{IS.psetup}")
    print(f"MANUAL: TFM:{IS.TFM}")
    print(f"AUTOMATIC: N:{IS.N}, T0:{IS.T0}, TFA:{IS.TFA}, TVA:{IS.TVA}, dn:{IS.dn}, p:{IS.p}")

def update_internal_state(IS):
    IS.N = IS.vals[0]
    IS.T0 = IS.vals[1]
    IS.TFA = IS.vals[2]
    IS.TVA = IS.vals[3]

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

    # state machine
    fsm = FSM(State.UNKNOWN)

    # create internal state object
    IS = InternalState()
    IS.changed = True

    while True:
        # read input keys
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break

        #--------------------------#
        # state machine transitions
        #--------------------------#
        # SETUP -> VIDEO
        if (fsm.state == State.SETUP) and \
           (k == SPACE) and (IS.psetup == 2):
            fsm.update(State.VIDEO)
        # VIDEO -> FREEZE
        elif (fsm.state == State.VIDEO) and \
             (k == ord('m')):
             fsm.update(State.FREEZE)
        # FREEZE -> VIDEO
        elif (fsm.state == State.FREEZE) and \
             (fsm.tis >= IS.TFM):
             fsm.update(State.VIDEO)
        # VIDEO -> PARAMS
        elif (fsm.state == State.VIDEO) and \
             (k == SPACE):
             fsm.update(State.PARAMS)
        # PARAMS -> VIDEO_AUTO
        elif (fsm.state == State.PARAMS) and \
             (k == SPACE) and (IS.p == 3):
             fsm.update(State.VIDEO_AUTO)
        # VIDEO_AUTO -> FREEZE_AUTO
        elif (fsm.state == State.VIDEO_AUTO) and \
             (((fsm.tis >= IS.TVA) and (IS.dn > 0)) or ((fsm.tis >= IS.T0) and (IS.dn > 0))):
             fsm.update(State.FREEZE_AUTO)
        # FREEZE_AUTO -> VIDEO_AUTO
        elif (fsm.state == State.FREEZE_AUTO) and \
             ((fsm.tis >= IS.TFA) and (IS.dn < IS.N)):
             fsm.update(State.VIDEO_AUTO)
        # FREEZE_AUTO -> VIDEO
        elif (fsm.state == State.FREEZE_AUTO) and \
             ((fsm.tis >= IS.TFA) and (IS.dn == IS.N)):
             fsm.update(State.VIDEO)
        # UNKNOWN -> SETUP
        elif state2string(fsm.state) == "UNKNOWN":
            fsm.update(State.SETUP)
        else:
            fsm.update(fsm.state) 

        #--------------------------#
        # state machine actions
        #--------------------------#
        if fsm.state == State.SETUP:

            # setting Type (intrinsics, extrinsics, targets)
            if IS.psetup == 0:
                # 'd' : increment t 
                if k == ord('d'):
                    IS.t = (IS.t+1)
                    if IS.t >= len(IS.Types):
                        IS.t = 0
                    IS.changed = True
                # 'a' : decrement t
                if k == ord('a'):
                    IS.t = IS.t - 1
                    if IS.t < 0:
                        IS.t = len(IS.Types)-1
                    IS.changed = True
            # id
            if IS.psetup == 1:
                # 'd' : increment id 
                if k == ord('d'):
                    IS.id = (IS.id+1)
                    if IS.id > 999999:
                        IS.id = 0
                    IS.changed = True
                # 'a' : decrement id
                if k == ord('a'):
                    IS.id = IS.id - 1
                    if IS.id < 0:
                        IS.id = 999999
                    IS.changed = True
            
            # TFM
            if IS.psetup == 2:
                # 'd' : increment TFM 
                if k == ord('d'):
                    IS.TFM = (IS.TFM+1)
                    if IS.TFM >= 60:
                        IS.TFM = 1
                    IS.changed = True
                # 'a' : decrement t
                if k == ord('a'):
                    IS.TFM = IS.TFM - 1
                    if IS.TFM < 1:
                        IS.TFM = 1
                    IS.changed = True
        elif fsm.state == State.VIDEO:
            pass

        elif fsm.state == State.FREEZE:
            # increment global frame count
            IS.n = IS.n+1
            IS.changed = True

        elif fsm.state == State.PARAMS:
            # N, T0, TFA, TVA
            if (IS.p >= 0) and (IS.p <= 3):
                # 'd' : increment value
                if k == ord('d'):
                    IS.vals[IS.p] += 1
                    update_internal_state(IS)
                    IS.changed = True
                elif k == ord('a'):
                    IS.vals[IS.p] -= 1
                    if IS.vals[IS.p] < 1:
                        IS.vals[IS.p] = 1
                    update_internal_state(IS)
                    IS.changed = True

        elif fsm.state == State.VIDEO_AUTO:
            pass
        elif fsm.state == State.FREEZE_AUTO:
            # increment global frame count
            IS.n += 1
            # increment automatic frame count
            IS.dn += 1
            IS.changed = True
        
        # printing state
        if fsm.state in (State.SETUP, State.PARAMS):
            if fsm.state != fsm.prev_state:
                
                print()
                print("FSM:")
                print(fsm)
                fsm.update_after_print()
        else:
            if fsm.should_print():
                print()
                print("FSM:")
                print(fsm)
                fsm.update_after_print()
        
        # printing internal state
        if IS.changed:
            print()
            print("IS:")
            print_internal_state(IS)
            IS.changed = False

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()