from utils import yaml as yml
from utils import paths as p
from pathlib import Path
from capture import CameraConfig, open_camera, capture_frame
import time
import cv2
import numpy as np

ROOT = p.get_root_dir(Path.cwd())
INPUTS = ROOT / "files" / "inputs"
GENERATED = ROOT / "files" / "generated"
OUTPUT_DIR = GENERATED / "capture"

ENTER = (10, 13)
SPACE = (32)

# capture frames settings and state variables
class CaptureFrames:
    def __init__(self,
                 display_seconds,
                 downsample_factor,
                 N_frames,
                 T_seconds,
                 T0_seconds):
        # default parameters, may change during runtime
        self.display_seconds = display_seconds
        self.downsample_factor = downsample_factor
        self.N_frames = N_frames
        self.T_seconds = T_seconds
        self.T0_seconds = T0_seconds
        # dynamic state
        self.last_frame = None
        self.last_time = None
        self.current_time = None

# camera information
class Camera:
    def __init__(self, cap, cam_config, w, h, downsample_factor):
        self.cap = cap
        self.cam_config = cam_config
        self.w = w
        self.h = h
        self.downsample_factor = downsample_factor

# current timestamp: YYYYMMDD_HHMMSS_ms
def current_timestamp():
    t = time.time()
    lt = time.localtime(t)
    ms = int((t - int(t)) * 1000)
    return time.strftime("%Y%m%d_%H%M%S", lt) + f"_{ms:03d}"

# load the camera object and the capture frames object
def load_configs():
    # load capture frames parameters
    cap_frames_config_dict = yml.load_file(INPUTS / "capture_frames.yaml")
    print(cap_frames_config_dict)
    # create capture frames config object
    cap_frames = CaptureFrames(**cap_frames_config_dict)
    print("loaded capture frames parameters.")
    for k, v in cap_frames_config_dict.items():
        print(f"{k}: {v}")
    # load camera parameters
    cam_config_dict = yml.load_file(INPUTS / "camera.yaml")
    # create camera config object
    cam_config = CameraConfig(**cam_config_dict)
    # open camera
    cap, w, h = open_camera(cam_config)
    # create the camera object
    cam = Camera(cap, cam_config, w, h, cap_frames.downsample_factor)
    return cam, cap_frames

# capture and display a frame,
# if frame is passed, use it instead of capturing a new frame
def video_feed(cam, frame = None, alpha=None, color=None):
    if frame is None:
        frame = capture_frame(cam.cap, cam.cam_config)
    # verify that the frame has the correct dimensions
    if frame.shape[:2] != (cam.h, cam.w):
        raise ValueError(f"frame shape {frame.shape[:2]} is different from expected shape {cam.w} x {cam.h}.")
    w_print, h_print = cam.w // cam.downsample_factor,cam.h // cam.downsample_factor
    frame = cv2.resize(frame, (w_print, h_print))
    if alpha is not None:
        frame = add_overlay(frame, alpha, color)
    cv2.imshow("frame", frame)

def add_overlay(frame, alpha=0.3, color=(0, 255, 0)):
    color_frame = np.zeros_like(frame)
    if color is None:
        color = (0, 255, 0)
    color_frame[:, :] = color # BGR (pure green)
    blended_frame = cv2.addWeighted(frame, 1 - alpha, color_frame, alpha, 0)
    return blended_frame

# update the capture frames object 
def last_captured_frame(cap_frames):
    # check if time to display frame has passed
    if cap_frames.last_frame is None:
        return None
    time_displayed = cap_frames.current_time - cap_frames.last_time
    if time_displayed > cap_frames.display_seconds:
        # reset last frame and time
        cap_frames.last_frame = None
        cap_frames.last_time = None
    return cap_frames.last_frame



def main():
    # load configs
    cam, cap_frames = load_configs()
    while True:
        # current time
        current_time = time.perf_counter()
        cap_frames.current_time = current_time
        # capture frame
        frame = capture_frame(cam.cap, cam.cam_config)
        # last captured frame
        lcframe = last_captured_frame(cap_frames)
        if lcframe is not None:
            video_feed(cam, lcframe, 0.3, (0, 255, 0))
        else:
            video_feed(cam, frame)

        # read the key pressed
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        # take frame when enter or space pressed
        if cap_frames.last_frame is None:
            if key in ENTER or key == SPACE:
                # save the frame
                cap_frames.last_frame = frame
                cap_frames.last_time = current_time

    # release the cap object
    cam.cap.release()
    # close the window
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

    