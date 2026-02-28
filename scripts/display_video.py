import cv2
import numpy as np
import platform
import yaml
from utils import get_project_root
from pathlib import Path

ROOT = get_project_root(Path.cwd())
CONFIG = ROOT / "config" / "camera_config.yaml"

class CameraConfig:
    def __init__(self,
                 wmax,
                 hmax,
                 w,
                 h,
                 rotation_deg,
                 x_is_mirrored,
                 x_should_be_mirrored,
                 y_is_mirrored,
                 y_should_be_mirrored,
                 fps):
        self.wmax = wmax
        self.hmax = hmax
        self.w = w
        self.h = h
        self.rotation_deg = rotation_deg
        self.x_flip = x_is_mirrored ^ x_should_be_mirrored
        self.y_flip = y_is_mirrored ^ y_should_be_mirrored
        self.fps = fps


def find_camera_index(camera_config, max_index = 10):
    wres = camera_config.wmax
    hres = camera_config.hmax 
    for index in range(max_index):
        cap, sys = open_camera(index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, wres)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, hres)
        w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        if w == wres and h == hres:
            return index
        raise RuntimeError(f"no matching camera with resolution {wres}x{hres} found.")

def open_camera(camera_config):
    camera_index = find_camera_index(camera_config)
    sys = platform.system()
    if sys == "Darwin": # mac
        cap = cv2.VideoCapture(camera_index, cv2.CAP_AVFOUNDATION)
        # set desired resolution
        w = int(camera_config.w)
        h = int(camera_config.h)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    elif sys == "Windows": # windows
        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        # reduce buffer to 1
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        # choose appropriate format for faster frame capture
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        # set desired resolution
        w = int(camera_config.w)
        h = int(camera_config.h)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        # set fps
        fps = camera_config.fps
        cap.set(cv2.CAP_PROP_FPS, fps)
    else:
        cap = cv2.VideoCapture(camera_index, 0) # use default for other OS (linux)
        # set desired resolution
        w = int(camera_config.w)
        h = int(camera_config.h)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    return cap, sys 

def rotate_frame(frame, camera_config):
    rotation_deg = camera_config.rotation_deg
    if rotation_deg == 90:
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    elif rotation_deg == 180:
        frame = cv2.rotate(frame, cv2.ROTATE_180)
    elif rotation_deg == 270:
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return frame

def flip_frame(frame, camera_config):
    mirror_x = camera_config.x_flip
    mirror_y = camera_config.y_flip
    if mirror_x and (not mirror_y):
        frame = cv2.flip(frame, 1)
    elif (not mirror_x) and mirror_y:
        frame = cv2.flip(frame, 0)
    elif mirror_x and mirror_y:
        frame = cv2.flip(frame, -1)
    return frame

def downsampled_dimensions(camera_config, downsample_factor):
    w = int(camera_config.w)
    h = int(camera_config.h)
    rotation_deg = camera_config.rotation_deg
    w_downsampled = w//downsample_factor
    h_downsampled = h//downsample_factor
    if rotation_deg in (90, 270):
        w_downsampled, h_downsampled = h_downsampled, w_downsampled
    return int(w_downsampled), int(h_downsampled)

def main():
    # load camera_config dictionary
    with open(CONFIG, "r") as f:
        camera_config_dict = yaml.safe_load(f)
    # create camera config object
    camera_config = CameraConfig(**camera_config_dict)
    # open camera
    cap, sys = open_camera(camera_config)
    print(f"opened camera, detected system {sys}")
    # display downsample
    downsample_factor = 4
    # downsampled dimensions
    w_display, h_display = downsampled_dimensions(camera_config, downsample_factor)
    print(f"downsampled to {w_display}x{h_display}.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("could not read frame.")
            break
        # rotate frame
        frame = rotate_frame(frame, camera_config)
        # flip frame
        frame = flip_frame(frame, camera_config)
        # downsample frame
        frame_display = cv2.resize(frame, (w_display, h_display))
        # display frame
        cv2.imshow("frame_display", frame_display)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()