import cv2
import numpy as np
import platform
import time
import copy

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

def open_configured_camera(cfg, warmup_frames = 5):
    wframes = []
    if warmup_frames < 1:
        warmup_frames = 1 # at least one to check the actual resolution being used
    sys = platform.system()
    if sys == "Darwin":
        print(f"OS: {sys}.")
        # camera object
        cap = cv2.VideoCapture(cfg.index, cv2.CAP_AVFOUNDATION)
        if not cap.isOpened():
            raise RuntimeError("camera did not open.")
        # resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.wreq)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.hreq)
        #  warmup frames
        print("warmup frames...")
        for i in range(warmup_frames):
            print(f"{i}/{warmup_frames}")
            ret, frame = cap.read()
            if not ret:
                raise RuntimeError("could not capture warmup frames.")
                wframes.append(frame)
        h, w = frame.shape[:2]
        print(f"opened camera: requested {cfg.wreq}x{cfg.hreq}, got {w}x{h}.")

    elif sys == "Windows":
        print(f"OS: {sys}.")
        # camera object
        cap = cv2.VideoCapture(cfg.index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            raise RuntimeError("camera did not open.")
        # data format
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG")) # FOUR Character Code, {MJPG, XVID, H264, ...}
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
        # fps
        if cfg.fps is not None:
            cap.set(cv2.CAP_PROP_FPS, cfg.fps)
        # resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.wreq)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.hreq)
        # reduce buffer
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        # warmup frames
        print("warmup frames...")
        for i in range(warmup_frames):
            print(f"{i}/{warmup_frames}")
            ret, frame = cap.read()
            if not ret:
                raise RuntimeError("could not capture warmup frames.")
            wframes.append(frame)
        h, w = frame.shape[:2]
        # set exposure manually {0.25: manual, 0.75:automatic}
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
        cap.set(cv2.CAP_PROP_EXPOSURE, -5) # 1/2^5 = 1/32 seconds -> fps limit is 32Hz
        print(f"opened camera: requested {cfg.wreq}x{cfg.hreq}, got {w}x{h}")
        print(f"fourcc (data compression):" + "".join([chr((fourcc>>8*i) & 0xFF) for i in range(4)]))
    else:
        print(f"OS: {sys}.")
        # camera object
        cap = cv2.VideoCapture(cfg.index, 0)
        if not cap.isOpened():
            raise RuntimeError("camera did not open.")
        # resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.wreq)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.hreq)
        # warmup frames
        print("warmup frames...")
        for i in range(warmup_frames):
            print(f"{i}/{warmup_frames}")
            ret, frame = cap.read()
            if not ret:
                raise RuntimeError("could not capture warmup frames.")
            wframes.append(frame)
        h, w = frame.shape[:2]
        print(f"opened camera: requested {cfg.wreq}x{cfg.hreq}, got {w}x{h}")
    return cap, wframes

def find_resolution_modes(cfg, f1=1, f2=4, N=40):
    # list of downsample factors to apply to max resolution
    f_list = [f1 + 1.0*i/N*(f2-f1) for i in range(N+1)]
    # copy of config object
    cfg_copy = copy.deepcopy(cfg)
    complete, distinct = []
    print(f"test resolution modes...")
    for i, f in enumerate(f_list):
        # set the resolution to be requested
        cfg_copy.wreq = int(cfg_copy.wmax/f)
        cfg_copy.hreq = int(cfg_copy.wmax/f)
        print(f"testing resolution {cfg_copy.wreq}x{cfg_copy.hreq} ({i}/{N})...")
        # open camera
        cap, wframes = open_configured_camera(cfg_copy, warmup_frames = 1)
        h, w = wframes[0].shape[:2]
        print(f"got {int(w)}x{int(h)}.")
        # append to complete list of actual resolutions
        complete.append((int(w), int(h)))
    # list of unique resolutions
    distinct = list(set(complete))
    print(f"finished test resolution modes.")
    return distinct, complete

def measure_fps(cap, T=3, warmup_frames = 3, T_print = 0.5):
    print("measure fps...")
    print("warmup frames...")
    # warmup frames:
    for i in range(warmup_frames):
        ret, frame = cap.read()
        if not ret:
            raise RuntimeError("could not capture warmup frames.")
    h, w = frame.shape[:2]
    print(f"testing resolution {itn(w)}x{int(h)}...")
    n = 0 # frame count
    dts = [] # times between frames
    t_start = time.perf_counter() # current time
    t_last_print = t_start - T_print - 0.1 # so that first frame is printed
    t_now = t
    while t_now - t_start < T:
        # read frame
        t1 = time.perf_counter()
        ret, frame = cap.read()
        t2 = time.perf_counter()
        dts.append(t2-t1)
        if not ret:
            raise RuntimeError("could not read frame.")
        n += 1 # accumulate frame count
        if t_now - t_last_print >= T_print:
            print(f"n = {n}, t = {t_now - t_start}.")
            t_last_print = t_now # update last print time
        t_now = time.perf_counter() # update current time
    if t_now - t_start > 1e-3:
        fps = n / (t_now-t_start)
    else:
        fps = 0
    print(f"n_total = {n}, t_total = {t_now-t_start}, fps = {fps}.")
    print(f"max dt = {max(dts)}, mean dt = {np.mean(dts)}, min dt = {min(dts)}")
    print("finished measure fps.")
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
