# python libraries
import cv2
import numpy as np
import yaml
import time
from pathlib import Path
from enum import Enum, auto
import copy

# my library
from utils import (
    get_project_root,
    RateMonitor,
    FSM,
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
DATASET = ROOT / ".." / "Datasets" / "image-pipeline"

# char codes
SPACE = 32

# FSM states
class States(Enum):
    SETUP = auto()
    VIDEO = auto()
    FREEZE = auto()

# Internal State
class IS:
    def __init__(self):
        self.k = None # key
        self.frame = None
        self.frame_to_save = None
        self.n = 0 # number of frames
        self.changed = True
        self.df = None # display frame object

def print_internal_state(internal_state):
    k = internal_state.k
    frame = internal_state.frame
    frame_to_save = internal_state.frame_to_save
    n = internal_state.n
    if internal_state.changed:
        print(f"k={k}, frame={'None' if frame is None else 'frame'}, frame_to_save={'None' if frame_to_save is None else 'frame'}, n={n}.")
        internal_state.changed = False
    
# FSM transitions
def fsm_transitions(fsm, internal_state):
    k = internal_state.k
    frame = internal_state.frame
    # SETUP -> VIDEO
    if (fsm.state == States.SETUP) and (k == SPACE):
        fsm.update(States.VIDEO)
    # VIDEO -> FREEZE
    elif (fsm.state == States.VIDEO) and (k == SPACE):
        internal_state.frame_to_save = copy.deepcopy(frame) # save current frame
        internal_state.changed = True
        fsm.update(States.FREEZE)
    # FREEZE -> VIDEO
    elif (fsm.state == States.FREEZE) and (k == SPACE):
        internal_state.frame_to_save = None
        internal_state.changed = True
        fsm.update(States.VIDEO)
    # VIDEO -> SETUP
    elif (fsm.state == States.VIDEO) and (k == ord('s')):
        fsm.update(States.SETUP)
    # FREEZE -> SETUP
    elif (fsm.state == States.FREEZE) and (k == ord('s')):
        fsm.update(States.SETUP)
    # UNKNOWN ->SETUP
    elif not isinstance(fsm.state, States):
        fsm.update(States.SETUP)

# fsm actions
def fsm_actions(fsm, internal_state):

    k = internal_state.k
    frame = internal_state.frame
    frame_to_save = internal_state.frame_to_save
    df = internal_state.df

    # SETUP
    if fsm.state == States.SETUP:
        # resize and display frame
        display_frame = get_display_frame(frame, df)
        cv2.imshow("display_frame", display_frame)
    # VIDEO
    elif fsm.state == States.VIDEO:
        # resize and display frame
        display_frame = get_display_frame(frame, df)
        cv2.imshow("display_frame", display_frame)
    # FREEZE
    elif fsm.state == States.FREEZE:
        # resize and display frame_to_save
        display_frame = get_display_frame(frame_to_save, df)
        # overlay with blue
        overlay = np.zeros_like(display_frame)
        blue = (255, 0, 0)
        overlay[:, :] = blue
        alpha = 0.3
        display_frame = cv2.addWeighted(overlay, alpha, display_frame, 1-alpha, 0)
        # display frame
        cv2.imshow("display_frame", display_frame)

    if fsm.prev_state is None or fsm.state != fsm.prev_state:
        # print current state
        if fsm.state is not None:
            print(f"state={fsm.state.name}.")
        else:
            print("state=UNKNOWN.")

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

    # fsm
    fsm = FSM(States.SETUP)

    # internal state
    internal_state = IS()
    internal_state.df = df

    # display the last warmup frame
    display_frame = get_display_frame(wframes[-1], df)
    cv2.imshow("display_frame", display_frame)

    while True:
        # read key
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break
        if (internal_state.k != k):
            internal_state.k = k
            internal_state.changed = True

        # read frame
        ret, frame = cap.read()
        if not ret:
            raise RuntimeError("could not read frame.")
        internal_state.frame = frame

        # fsm transitions
        fsm_transitions(fsm, internal_state)

        # fsm_actions
        fsm_actions(fsm, internal_state)

        fsm.update(fsm.state)

        # print internal state
        print_internal_state(internal_state)

        # rate monitor
        rate_monitor.increment(time.perf_counter())

    cap.release()
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()