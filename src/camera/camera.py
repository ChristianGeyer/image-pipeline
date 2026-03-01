import cv2
import numpy as np
import platform
import time

class CameraConfig:
    def __init__(self,
                 wmax,
                 hmax,
                 wreq,
                 hreq,
                 rotation_deg,
                 x_is_mirrored,
                 x_should_be_mirrored,
                 y_is_mirrored,
                 y_should_be_mirrored,
                 fps,
                 index):
        self.wmax = wmax
        self.hmax = hmax
        self.wreq = wreq
        self.hreq = hreq
        self.rotation_deg = rotation_deg
        self.x_flip = x_is_mirrored ^ x_should_be_mirrored
        self.y_flip = y_is_mirrored ^ y_should_be_mirrored
        self.fps = fps
        self.index = 0
        if index is not None:
            self.index = index

# cfg : CameraConfig object
def open_camera_by_index(cfg):
    sys = platform.system()
    if sys == "Darwin":
        cap = cv2.VideoCapture(cfg.index, cv2.CAP_AVFOUNDATION)
    elif sys == "Windows":
        cap = cv2.VideoCapture(cfg.index, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(cfg.index, 0)
    # test if capture object opened
    if not cap.isOpened():
        raise RuntimeError(f"{sys} could not open usb camera at index {cfg.index}.")
    return cap


# test resolution modes
# test from (wmax, hmax)/f1 to (wmax,hmax)/f2
def test_resolution_modes(cfg, f1, f2, N):
    # open VideoCapture Object
    cap = open_camera_by_index(cfg)

    distinct = []
    complete = []
    for i in range(N+1):
        print(f"{i}/{N}")
        f = f1 + 1.0*i*(f2-f1)/N
        # request resolution
        wreq = int(cfg.wmax/f)
        hreq = int(cfg.hmax/f)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, wreq)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, hreq)
        # capture frame
        ret, frame = cap.read()
        h, w = frame.shape[:2]
        complete.append((wreq, hreq, w, h))
        if (w, h) not in set(distinct):
            distinct.append((w, h))
    cap.release()
    return distinct, complete

# test fps of a resolution mode
def test_resolution_mode_fps(cap, mode, T=10, warmup_frames=5):
    wreq, hreq = mode
    wreq = int(wreq)
    hreq = int(hreq)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, wreq)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, hreq)
    print(f"testing mode {wreq}x{hreq}.")
    # warmup frames
    for i in range(warmup_frames):
        ret, frame = cap.read()
    # check frame shape
    print(f"frame shape: {frame.shape[1]}x{frame.shape[0]}.")
    # frame count
    n = 0
    # initial time
    t = time.perf_counter()
    # read times
    dts = []
    tprint = t
    while time.perf_counter() - t < T:
        t1 = time.perf_counter()
        if t1-tprint > 1:
            print(f"{np.round(t1-t, 3)}s/{T}s")
            tprint = t1
        ret, frame = cap.read()
        dt = time.perf_counter()-t1
        dts.append(dt)
        n = n+1
    fps = n / (time.perf_counter()-t)
    return fps, dts

def rotate_frame(frame, cfg):
    rotation_deg = cfg.rotation_deg
    if rotation_deg == 90:
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    elif rotation_deg == 180:
        frame = cv2.rotate(frame, cv2.ROTATE_180)
    elif rotation_deg == 270:
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return frame

def flip_frame(frame, cfg):
    mirror_x = cfg.x_flip
    mirror_y = cfg.y_flip
    if mirror_x and (not mirror_y):
        frame = cv2.flip(frame, 1)
    elif (not mirror_x) and mirror_y:
        frame = cv2.flip(frame, 0)
    elif mirror_x and mirror_y:
        frame = cv2.flip(frame, -1)
    return frame
