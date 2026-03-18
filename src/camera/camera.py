import cv2
import numpy as np

def open_camera(camera_index: int, driver: str | None = None) -> cv2.VideoCapture:
    """
    Open a camera using OpenCV.

    If no driver is specified, OpenCV selects the default backend for the OS.
    If a driver is provided, it is mapped to the corresponding OpenCV backend.

    Args:
        camera_index: Index of the camera device.
        driver: Optional backend/driver name (e.g., 'dshow', 'avfoundation', 'v4l2').

    Returns:
        Opened cv2.VideoCapture object.

    Raises:
        RuntimeError: If the camera cannot be opened.
    """
    driver_map = {
        "dshow": cv2.CAP_DSHOW,
        "avfoundation": cv2.CAP_AVFOUNDATION,
        "v4l2": cv2.CAP_V4L2,
        "msmf": cv2.CAP_MSMF,
    }

    if driver is None:
        cap = cv2.VideoCapture(camera_index)
    else:
        backend = driver_map.get(driver.lower())
        if backend is None:
            raise ValueError(f"Unknown driver: {driver}")
        cap = cv2.VideoCapture(camera_index, backend)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera (index={camera_index}, driver={driver})")

    return cap


def set_resolution(
    cap: cv2.VideoCapture,
    width: int | None,
    height: int | None,
) -> tuple[int, int]:
    """
    Set the camera capture resolution if specified.

    Args:
        cap: OpenCV VideoCapture object.
        width: Desired frame width in pixels.
        height: Desired frame height in pixels.

    Returns:
        Tuple (actual_width, actual_height) after applying settings.
    """
    if width is not None:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)

    if height is not None:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    return actual_width, actual_height


def read_frame(cap: cv2.VideoCapture) -> np.ndarray:
    """
    Capture a single frame from the camera.

    Args:
        cap: OpenCV VideoCapture object.

    Returns:
        Captured frame as a NumPy array.

    Raises:
        RuntimeError: If a frame cannot be read.
    """
    ret, frame = cap.read()

    if not ret or frame is None:
        raise RuntimeError("Failed to read frame from camera.")

    return frame


def rotate_frame(frame: np.ndarray, angle: int) -> np.ndarray:
    """
    Rotate a frame by a given angle (in degrees).

    Supported angles: 0, 90, 180, 270.

    Args:
        frame: Input image frame.
        angle: Rotation angle in degrees.

    Returns:
        Rotated frame.

    Raises:
        ValueError: If angle is not supported.
    """
    if angle == 0:
        return frame
    elif angle == 90:
        return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        return cv2.rotate(frame, cv2.ROTATE_180)
    elif angle == 270:
        return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    else:
        raise ValueError(f"Unsupported rotation angle: {angle}")
    

def flip_frame(frame: np.ndarray, flip_x: bool, flip_y: bool) -> np.ndarray:
    """
    Flip a frame horizontally and/or vertically.

    Args:
        frame: Input image frame.
        flip_x: If True, flip horizontally.
        flip_y: If True, flip vertically.

    Returns:
        Flipped frame.
    """
    if flip_x and flip_y:
        return cv2.flip(frame, -1)
    elif flip_x:
        return cv2.flip(frame, 1)
    elif flip_y:
        return cv2.flip(frame, 0)
    else:
        return frame


def resize_frame(
    frame: np.ndarray,
    width: int | None,
    height: int | None,
) -> np.ndarray:
    """
    Resize a frame while preserving aspect ratio.

    If both width and height are given, they are treated as a bounding box and
    the frame is scaled to fit inside it without cropping or distortion.

    Args:
        frame: Input image frame.
        width: Maximum target width in pixels.
        height: Maximum target height in pixels.

    Returns:
        Resized frame.
    """
    if width is None and height is None:
        return frame

    original_h, original_w = frame.shape[:2]

    if width is not None and height is not None:
        scale = min(width / original_w, height / original_h)
        new_w = max(1, int(round(original_w * scale)))
        new_h = max(1, int(round(original_h * scale)))

    elif width is not None:
        scale = width / original_w
        new_w = width
        new_h = max(1, int(round(original_h * scale)))

    else:
        scale = height / original_h
        new_w = max(1, int(round(original_w * scale)))
        new_h = height

    return cv2.resize(frame, (new_w, new_h))