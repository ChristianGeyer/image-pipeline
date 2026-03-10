import cv2
import numpy as np
from capture import open_camera, capture_frame, CameraConfig
from utils import yaml as yml
from utils import paths as p
from pathlib import Path
import time


#---------------#
# Constants
#---------------#
ROOT = p.get_root_dir(Path.cwd())
INPUTS = ROOT / "files" / "inputs"

ENTER = (10, 13)
SPACE = 32

T_FREEZE_SECONDS = 1.0 # seconds

STATES = [
     "video",
     "freeze",
]

#--------------#
# Finite State Machine class
#--------------#
class FSM:
    def __init__(self, state):
        self.state = state
        self.tes = time.perf_counter()
        self.tis = 0.0
    def update(self, state):
        if self.state == state:
            self.tis = time.perf_counter() - self.tes
        else:
            self.tes = time.perf_counter()
            self.tis = 0.0
            self.state = state

#--------------#
# Control Loop class
#--------------#
class ControlLoop:
    def __init__(self, Ts):
        self.Ts = Ts
        self.tel = 0.0 # time entering loop
    
    def enter_loop(self):
        t_curr = time.perf_counter()
        if t_() - self.tel > self.Ts:
            self.tel = time.perf_counter()
            return True
        else:
            return False

def main():
    # load camera params from yaml file
    cam_config_dict = yml.load_file(INPUTS / "camera.yaml")
    # create camera config object
    cam_config = CameraConfig(**cam_config_dict)
    # open camera
    cap, w, h = open_camera(cam_config)
    # display resolution
    downsample_factor = 4
    w_display, h_display = w // downsample_factor, h // downsample_factor
    print(f"opened camera with resolution: {w} x {h}")
    print(f"display resolution: {w_display} x {h_display}")
    print("starting video feed. press 'q' to quit.")

    # start with the video feed
    fsm = FSM("video")

    saved_frame = None

    while True:
        # read inputs
        k = cv2.waitKey(1) & 0xFF

        # state transitions
        if (fsm.state == " video") and (k == ord('f')):
            fsm.update("freeze")
        # quit
        if k == ord('q'):
            break
        # freeze frame
        if k == ord('f'):
            saved_frame = capture_frame(cap, cam_config)
            saved_time = time.perf_counter()

        



        # current time
        t_curr = time.perf_counter()
        # capture frame
        frame = capture_frame(cap, cam_config)
       
        # quit
        if k == ord('q'):
             break
        elif (k in ENTER) or (k==SPACE):
             saved_frame = frame
             saved_time = t_curr
             display_frame(saved_frame, w, h, downsample_factor)

        if saved_frame is None and display_loop.enter_loop(t_curr):
            # resize (downsample)
            frame = cv2.resize(frame, (w_print, h_print))
            # display
            cv2.imshow("frame", frame)
        # keys
        k = cv2.waitKey(1) & 0xFF
        # quit
        if k == ord('q'):
            break
        # save frame
        if (saved_frame is None) and (k in ENTER) or (k in SPACE):
            # save the frame  
            saved_frame = frame
            saved_time = t_curr
            green_background = np.zeros_like(frame)
            green_background[:, :] = (0, 255, 0)
            saved_frame = cv2.addWeighted(frame, 0.7, green_background, 0.3, 0)
            cv2.imshow("captured frame", saved_frame)
        elif t_curr - saved_time > 1.0:
                saved_frame = None
        
    
    cap.release()
    cv2.destroyAllWindows()
    print("closed camera.")

if __name__ == "__main__":
    main()