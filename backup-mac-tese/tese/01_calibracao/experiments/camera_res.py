import cv2
import time
import numpy as np

def measure_capture_timing(requested_width, requested_height, camera_index=0):
    """
    Requests a resolution, captures 10 frames,
    returns (actual_width, actual_height, mean_dt_seconds, approx_fps)
    """

    cap = cv2.VideoCapture(camera_index, cv2.CAP_AVFOUNDATION)

    if not cap.isOpened():
        raise RuntimeError("Could not open camera.")

    # Request resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, requested_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, requested_height)

    # Give camera time to settle
    time.sleep(0.5)

    timestamps = []
    frames_captured = 0

    while frames_captured < 10:
        ret, frame = cap.read()
        if not ret:
            continue

        timestamps.append(time.perf_counter())
        frames_captured += 1

    cap.release()

    # Compute time differences between consecutive frames
    diffs = np.diff(timestamps)

    mean_dt = float(np.mean(diffs))
    approx_fps = 1.0 / mean_dt if mean_dt > 0 else 0.0

    actual_height, actual_width = frame.shape[:2]

    return actual_width, actual_height, mean_dt, approx_fps

