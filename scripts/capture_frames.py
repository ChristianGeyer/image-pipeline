import argparse
from enum import Enum
import cv2

from camera import (
    open_camera,
    set_resolution,
    read_frame,
    rotate_frame,
    flip_frame,
    resize_frame,
)
from utils import (
    get_project_root,
    CycleCounter,
    FSM,
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


class CaptureState(Enum):
    VIDEO = "VIDEO"
    FREEZE = "FREEZE"


def read_inputs() -> int:
    """
    Read the current keyboard input.

    Returns:
        Integer key code from OpenCV.
    """
    return cv2.waitKey(1) & 0xFF


def apply_transitions(fsm: FSM, key: int) -> None:
    """
    Apply state transitions based on the current inputs and time in state.

    Transitions:
        VIDEO --[space]--> FREEZE
        FREEZE --[tis >= 1]--> VIDEO

    Args:
        fsm: Finite state machine.
        key: Current keyboard input.
    """
    previous_state = fsm.state

    if fsm.state == CaptureState.VIDEO:
        if key == ord(" "):
            fsm.update(CaptureState.FREEZE)

    elif fsm.state == CaptureState.FREEZE:
        if fsm.tis >= 1.0:
            fsm.update(CaptureState.VIDEO)

    if fsm.state != previous_state:
        print(f"State changed to: {fsm.state.value}")


def apply_actions(
    fsm: FSM,
    cap: cv2.VideoCapture,
    freeze_frame,
    rotate: int,
    flip_x: bool,
    flip_y: bool,
    display_width: int,
    display_height: int,
):
    """
    Apply state-dependent actions and return the frame to display.

    In VIDEO state:
        - Read and process the current frame.
    In FREEZE state:
        - On first entry, capture and store one frame.
        - Keep displaying the stored frame without overwriting it.

    Args:
        fsm: Finite state machine.
        cap: OpenCV VideoCapture object.
        freeze_frame: Currently stored frozen frame, or None.
        rotate: Rotation angle in degrees.
        flip_x: Whether to flip horizontally.
        flip_y: Whether to flip vertically.
        display_width: Display bounding width.
        display_height: Display bounding height.

    Returns:
        Tuple (frame_to_display, updated_freeze_frame).
    """
    if fsm.state == CaptureState.VIDEO:
        frame = read_frame(cap)
        frame = rotate_frame(frame, rotate)
        frame = flip_frame(frame, flip_x, flip_y)
        frame = resize_frame(frame, display_width, display_height)
        return frame, None

    if fsm.state == CaptureState.FREEZE:
        if freeze_frame is None:
            freeze_frame = read_frame(cap)
            freeze_frame = rotate_frame(freeze_frame, rotate)
            freeze_frame = flip_frame(freeze_frame, flip_x, flip_y)
            freeze_frame = resize_frame(freeze_frame, display_width, display_height)

        return freeze_frame, freeze_frame

    raise ValueError(f"Unsupported state: {fsm.state}")


def main() -> None:
    """
    Run the capture-frames script with VIDEO and FREEZE states.

    VIDEO:
        Continuously display the live video feed.

    FREEZE:
        Capture and store the first frame on entry, display it without updating,
        and return to VIDEO after 1 second.

    Press:
        - space: transition from VIDEO to FREEZE
        - q: quit
    """
    args = parse_args()
    project_root = get_project_root(None)

    cap = open_camera(args.camera_index, args.driver)
    set_resolution(cap, args.pixels_width, args.pixels_height)

    display_width = 300
    display_height = 300

    fsm = FSM(CaptureState.VIDEO)
    freeze_frame = None

    print(f"Project root: {project_root}")
    print(f"State changed to: {fsm.state.value}")

    try:
        while True:
            key = read_inputs()

            if key == ord("q"):
                break

            apply_transitions(fsm, key)

            if fsm.state == CaptureState.VIDEO:
                freeze_frame = None

            frame, freeze_frame = apply_actions(
                fsm=fsm,
                cap=cap,
                freeze_frame=freeze_frame,
                rotate=args.rotate,
                flip_x=args.flip_x,
                flip_y=args.flip_y,
                display_width=display_width,
                display_height=display_height,
            )

            cv2.imshow("Capture Frames", frame)

    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()