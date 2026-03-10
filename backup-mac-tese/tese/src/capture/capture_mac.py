# capture/capture_mac.py
import time
import cv2
import numpy as np

class CameraConfig:
    def __init__(self, 
                 camera_index, 
                 size,
                 warmup_frames,
                 warmup_seconds, 
                 rotate_deg):
        self.camera_index = camera_index
        self.size = size
        self.warmup_frames = warmup_frames
        self.warmup_seconds = warmup_seconds
        self.rotate_deg = rotate_deg

def open_camera(cam_config):
    # extract camera config parameters
    camera_index = cam_config.camera_index
    requested_size = cam_config.size
    warmup_frames = cam_config.warmup_frames
    warmup_seconds = cam_config.warmup_seconds
    rotate_deg = cam_config.rotate_deg
    # size dimensions 
    req_w, req_h = requested_size
    # open camera
    cap = cv2.VideoCapture(camera_index, cv2.CAP_AVFOUNDATION)
    if not cap.isOpened():
        raise RuntimeError(f"could not open camera index {camera_index} using AVFoundation.")
    # request resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(req_w))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(req_h))
    # warmup seconds
    if warmup_seconds > 0:
        time.sleep(float(warmup_seconds))
    # warmup frames
    for _ in range(warmup_frames):
        ret, frame = cap.read()
        if not ret or frame is None:
            raise RuntimeError("failed to capture frame from camera.")
    # actual size
    h, w = frame.shape[:2]
    if rotate_deg in (90, 270):
        h, w = w, h
    return cap, int(w), int(h)
        
def capture_frame(cap, camera_config):
    rotate_deg = camera_config.rotate_deg
    if rotate_deg not in (0, 90, 180, 270):
        raise ValueError(f"rotate_deg {rotate_deg} not in {[0, 90, 180, 270]}")
    ret, frame = cap.read()
    if not ret or frame is None:
        raise RuntimeError("failed to capture frame from camera.")
    if rotate_deg == 90:
        return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    elif rotate_deg == 180:
        return cv2.rotate(frame, cv2.ROTATE_180)
    elif rotate_deg == 270:
        return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return frame