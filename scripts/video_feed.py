import argparse
import cv2
import numpy as np

from utils import get_project_root, CycleCounter


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for configuring the video feed.

    Supported arguments:
        --camera-index: Index of the camera device to open (default: 0).
        --pixels-width: Requested frame width in pixels.
        --pixels-height: Requested frame height in pixels.
        --driver: Backend/driver to use (e.g., 'dshow', 'avfoundation', 'v4l2').
        --rotate: Rotation to apply to frames in degrees (0, 90, 180, 270).
        --flip-x: If set, flip frames horizontally.
        --flip-y: If set, flip frames vertically.

    Returns:
        argparse.Namespace containing the parsed argument values.
    """

    parser = argparse.ArgumentParser(
        description="Video feed script (argument parsing only)."
    )

    parser.add_argument(
        "--camera-index",
        type=int,
        default=0,
        help="Camera device index (default: 0)",
    )

    parser.add_argument(
        "--pixels-width",
        type=int,
        default=None,
        help="Requested frame width in pixels",
    )

    parser.add_argument(
        "--pixels-height",
        type=int,
        default=None,
        help="Requested frame height in pixels",
    )

    parser.add_argument(
        "--driver",
        type=str,
        default=None,
        help="Camera backend/driver (e.g., dshow, avfoundation, v4l2)",
    )

    parser.add_argument(
        "--rotate",
        type=int,
        default=0,
        help="Rotation in degrees (e.g., 0, 90, 180, 270)",
    )

    parser.add_argument(
        "--flip-x",
        action="store_true",
        help="Flip frame horizontally",
    )

    parser.add_argument(
        "--flip-y",
        action="store_true",
        help="Flip frame vertically",
    )

    return parser.parse_args()

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


def main() -> None:
    """
    Entry point for the video feed script.

    Parses arguments, opens the camera, applies the requested resolution,
    performs a warmup, and displays the processed video stream until 'q' is pressed.
    """
    import cv2

    args = parse_args()
    project_root = get_project_root(None)

    cap = open_camera(args.camera_index, args.driver)
    requested_width = args.pixels_width
    requested_height = args.pixels_height
    actual_capture_width, actual_capture_height = set_resolution(
        cap,
        requested_width,
        requested_height,
    )

    display_width = 300
    display_height = 300
    warmup_frames = 5

    frame = None
    for _ in range(warmup_frames):
        frame = read_frame(cap)

    if frame is None:
        raise RuntimeError("Failed to read warmup frames from camera.")

    original_height, original_width = frame.shape[:2]

    rotated_frame = rotate_frame(frame, args.rotate)
    rotated_height, rotated_width = rotated_frame.shape[:2]

    flipped_frame = flip_frame(rotated_frame, args.flip_x, args.flip_y)
    resized_frame = resize_frame(flipped_frame, display_width, display_height)
    resized_height, resized_width = resized_frame.shape[:2]

    print("=== Video Feed Configuration ===")
    print(f"Project root              : {project_root}")
    print(f"Camera index              : {args.camera_index}")
    print(f"Requested width           : {requested_width}")
    print(f"Requested height          : {requested_height}")
    print(f"Driver                    : {args.driver}")
    print(f"Rotate                    : {args.rotate}")
    print(f"Flip X                    : {args.flip_x}")
    print(f"Flip Y                    : {args.flip_y}")
    print(f"Actual capture width      : {actual_capture_width}")
    print(f"Actual capture height     : {actual_capture_height}")
    print(f"Original frame width      : {original_width}")
    print(f"Original frame height     : {original_height}")
    print(f"Rotated frame width       : {rotated_width}")
    print(f"Rotated frame height      : {rotated_height}")
    print(f"Resized frame width       : {resized_width}")
    print(f"Resized frame height      : {resized_height}")
    print(f"Display width bound       : {display_width}")
    print(f"Display height bound      : {display_height}")

    try:
        counter = CycleCounter()
        while True:
            frame = read_frame(cap)
            frame = rotate_frame(frame, args.rotate)
            frame = flip_frame(frame, args.flip_x, args.flip_y)
            frame = resize_frame(frame, display_width, display_height)

            cv2.imshow("Video Feed", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            counter.tick()
            
            # print and reset every 5 seconds
            if counter.elapsed_time >= 5.0:
                count, elapsed, freq = counter.snapshot()
                print(f"{count} cycles in {elapsed:.2f}s → {freq:.2f} Hz")
                counter.reset()
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()