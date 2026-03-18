import argparse
import cv2
import numpy as np

from utils import (
    get_project_root, 
    CycleCounter,
)

from camera import (
    open_camera,
    set_resolution,
    read_frame,
    rotate_frame,
    flip_frame,
    resize_frame,
)


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