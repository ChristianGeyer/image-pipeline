import argparse
import shutil
from enum import Enum, auto
from pathlib import Path

import cv2
import numpy as np

from camera import (
    flip_frame,
    open_camera,
    read_frame,
    resize_frame,
    rotate_frame,
    set_resolution,
)
from utils import FSM, get_project_root


class CaptureState(Enum):
    VIDEO = auto()
    FREEZE = auto()


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for configuring the video feed.

    Supported arguments:
        --camera-index: Index of the camera device to open. Default: 0.
        --pixels-width: Requested capture width in pixels.
        --pixels-height: Requested capture height in pixels.
        --display-width: Display bounding width in pixels. Default: 300.
        --display-height: Display bounding height in pixels. Default: 300.
        --driver: Backend/driver to use.
        --rotate: Rotation to apply to frames in degrees. Allowed: 0, 90, 180, 270.
        --flip-x: If set, flip frames horizontally.
        --flip-y: If set, flip frames vertically.

    Returns:
        Namespace containing the parsed argument values.
    """
    parser = argparse.ArgumentParser(description="Display video and capture frozen frames.")

    parser.add_argument("--camera-index", type=int, default=0)
    parser.add_argument("--pixels-width", type=int, default=None)
    parser.add_argument("--pixels-height", type=int, default=None)

    parser.add_argument("--display-width", type=int, default=300)
    parser.add_argument("--display-height", type=int, default=300)

    parser.add_argument("--driver", type=str, default=None)
    parser.add_argument("--rotate", type=int, default=0, choices=[0, 90, 180, 270])
    parser.add_argument("--flip-x", action="store_true")
    parser.add_argument("--flip-y", action="store_true")

    return parser.parse_args()

def read_inputs() -> int:
    """
    Read the current keyboard input.

    Returns:
        Integer key code from OpenCV.
    """
    return cv2.waitKey(1) & 0xFF


def apply_transitions(fsm: FSM, key: int) -> None:
    """
    Apply state transitions based on keyboard input.

    Transitions:
        VIDEO  --[space]--> FREEZE
        FREEZE --[space]--> VIDEO

    Args:
        fsm: Finite state machine.
        key: Current keyboard input.
    """
    if key == ord(" "):
        if fsm.state == CaptureState.VIDEO:
            fsm.update(CaptureState.FREEZE)
        else:
            fsm.update(CaptureState.VIDEO)


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
        - Read one frame.
        - Rotate it.
        - Flip it.
        - Resize it to fit within the display bounds.
        - Do not keep a frozen frame.

    In FREEZE state:
        - If `freeze_frame` is None, read and process one frame once using the
          same rotate/flip/resize order as VIDEO, then store it.
        - Reuse the stored frame on later iterations without overwriting it.

    Args:
        fsm: Finite state machine.
        cap: OpenCV VideoCapture object.
        freeze_frame: Stored frozen frame, or None.
        rotate: Rotation angle in degrees.
        flip_x: Whether to flip horizontally.
        flip_y: Whether to flip vertically.
        display_width: Display bounding width.
        display_height: Display bounding height.

    Returns:
        Tuple `(frame_to_display, updated_freeze_frame)`.
    """
    if fsm.state == CaptureState.VIDEO:
        frame = read_frame(cap)
        frame = rotate_frame(frame, rotate)
        frame = flip_frame(frame, flip_x, flip_y)
        frame = resize_frame(frame, display_width, display_height)
        return frame, None

    if freeze_frame is None:
        freeze_frame = read_frame(cap)
        freeze_frame = rotate_frame(freeze_frame, rotate)
        freeze_frame = flip_frame(freeze_frame, flip_x, flip_y)
        freeze_frame = resize_frame(freeze_frame, display_width, display_height)

    return freeze_frame, freeze_frame


def prepare_output_dir() -> Path:
    """
    Create an empty `capture_frames_output` directory at the project root.

    Behavior:
        - Resolve the project root from this script path.
        - Remove `capture_frames_output/` if it already exists.
        - Recreate the directory empty.

    Returns:
        Path to the prepared output directory.
    """
    project_root = get_project_root(__file__)
    output_dir = project_root / "capture_frames_output"

    if output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def save_freeze_frame(freeze_frame, output_dir: Path, image_index: int) -> Path:
    """
    Save the frozen frame as `imgXXXX.png`.

    Behavior:
        - Build the output path as `img{image_index:04d}.png`.
        - Write `freeze_frame` with OpenCV.
        - Raise an error if writing fails.

    Args:
        freeze_frame: Frame to save.
        output_dir: Output directory.
        image_index: 1-based image index.

    Returns:
        Path to the saved image.

    Raises:
        RuntimeError: If the image cannot be written.
    """
    output_path = output_dir / f"img{image_index:04d}.png"
    ok = cv2.imwrite(str(output_path), freeze_frame)
    if not ok:
        raise RuntimeError(f"Failed to save image to {output_path}")
    return output_path


def _apply_region_overlay(
    frame: np.ndarray,
    top_left: tuple[int, int],
    bottom_right: tuple[int, int],
    color: tuple[int, int, int],
    alpha: float,
) -> np.ndarray:
    """
    Return a copy of `frame` with a color overlay applied only to one region.

    Args:
        frame: Input frame.
        top_left: Inclusive `(x, y)` top-left corner of the region.
        bottom_right: Exclusive `(x, y)` bottom-right corner of the region.
        color: Overlay color in OpenCV BGR order.
        alpha: Overlay alpha in `[0.0, 1.0]`.

    Returns:
        Frame copy with the region tinted.
    """
    result = frame.copy()

    x0 = max(0, min(frame.shape[1], top_left[0]))
    y0 = max(0, min(frame.shape[0], top_left[1]))
    x1 = max(0, min(frame.shape[1], bottom_right[0]))
    y1 = max(0, min(frame.shape[0], bottom_right[1]))

    if x0 >= x1 or y0 >= y1:
        return result

    roi = result[y0:y1, x0:x1]
    overlay = np.empty_like(roi)
    overlay[:] = color
    result[y0:y1, x0:x1] = cv2.addWeighted(overlay, alpha, roi, 1.0 - alpha, 0.0)
    return result


def _compute_last_saved_label_geometry(
    frame: np.ndarray,
    last_saved_index: int,
) -> dict:
    """
    Compute text and background geometry for the last-saved label.

    Args:
        frame: Frame on which the label will be drawn.
        last_saved_index: Last saved image index.

    Returns:
        Dictionary containing the text, font settings, text origin, and
        background rectangle coordinates.
    """
    text = f"last saved: {last_saved_index:04d}"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 2
    margin = 10
    padding_x = 8
    padding_y = 6

    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)

    text_x = max(margin, frame.shape[1] - text_width - margin)
    text_y = margin + text_height

    rect_x0 = max(0, text_x - padding_x)
    rect_y0 = max(0, text_y - text_height - padding_y)
    rect_x1 = min(frame.shape[1], text_x + text_width + padding_x)
    rect_y1 = min(frame.shape[0], text_y + baseline + padding_y)

    return {
        "text": text,
        "font": font,
        "font_scale": font_scale,
        "thickness": thickness,
        "text_origin": (text_x, text_y),
        "rect_top_left": (rect_x0, rect_y0),
        "rect_bottom_right": (rect_x1, rect_y1),
    }


def _apply_freeze_overlay(
    frame: np.ndarray,
    text_rect_top_left: tuple[int, int],
    text_rect_bottom_right: tuple[int, int],
    alpha: float = 0.3,
) -> np.ndarray:
    """
    Return a copy of `frame` tinted for FREEZE display.

    Behavior:
        - Apply a blue overlay with alpha `0.3` to the whole frame.
        - Apply a green overlay with the same alpha to the text background
          region.
        - The text region is tinted from the original frame, not from the
          already-blue frame, so the overlays are not mixed there.

    Args:
        frame: Input frame.
        text_rect_top_left: Inclusive top-left corner of the text region.
        text_rect_bottom_right: Exclusive bottom-right corner of the text region.
        alpha: Overlay alpha.

    Returns:
        Tinted frame for FREEZE display.
    """
    overlay_blue = np.empty_like(frame)
    overlay_blue[:] = (255, 0, 0)
    result = cv2.addWeighted(overlay_blue, alpha, frame, 1.0 - alpha, 0.0)

    x0, y0 = text_rect_top_left
    x1, y1 = text_rect_bottom_right

    x0 = max(0, min(frame.shape[1], x0))
    y0 = max(0, min(frame.shape[0], y0))
    x1 = max(0, min(frame.shape[1], x1))
    y1 = max(0, min(frame.shape[0], y1))

    if x0 < x1 and y0 < y1:
        original_roi = frame[y0:y1, x0:x1]
        overlay_green = np.empty_like(original_roi)
        overlay_green[:] = (0, 255, 0)
        result[y0:y1, x0:x1] = cv2.addWeighted(
            overlay_green,
            alpha,
            original_roi,
            1.0 - alpha,
            0.0,
        )

    return result


def _draw_last_saved_index(frame: np.ndarray, last_saved_index: int) -> np.ndarray:
    """
    Return a copy of `frame` with the last saved index drawn at the top-right.

    Behavior:
        - Draw a green semi-transparent background rectangle behind the label.
        - Draw the label text over that rectangle.

    Args:
        frame: Input frame.
        last_saved_index: Last saved image index.

    Returns:
        Annotated frame.
    """
    geometry = _compute_last_saved_label_geometry(frame, last_saved_index)

    annotated = _apply_region_overlay(
        frame=frame,
        top_left=geometry["rect_top_left"],
        bottom_right=geometry["rect_bottom_right"],
        color=(0, 255, 0),
        alpha=0.3,
    )

    cv2.putText(
        annotated,
        geometry["text"],
        geometry["text_origin"],
        geometry["font"],
        geometry["font_scale"],
        (255, 255, 255),
        geometry["thickness"],
        cv2.LINE_AA,
    )
    return annotated


def main() -> None:
    """
    Run the capture-frames script with VIDEO and FREEZE states.

    Behavior:
        1. Parse arguments.
        2. Create an empty `capture_frames_output/` directory at startup.
        3. Open the camera and apply the requested capture resolution.
        4. Start in VIDEO state.
        5. In VIDEO:
           - read, rotate, flip, and resize live frames
           - display the live frame
           - if space is pressed, transition to FREEZE
        6. In FREEZE:
           - capture one processed frame once on entry
           - display that stored frame with a blue overlay of alpha 0.3
           - display the text background region with a green overlay of alpha
             0.3 instead of blue, without mixing the two overlays there
           - if `s` is pressed and the current frozen frame has not yet been
             saved, save the untinted frozen frame as `imgXXXX.png`, update the
             last saved index, mark the frame as already saved, and transition
             to VIDEO
           - additional `s` presses must not save the same frozen frame again
           - if space is pressed, transition to VIDEO without saving
        7. Draw the last saved index at the top-right corner of every displayed
           frame with a green semi-transparent background. Before any save, the
           displayed value is `0000`.
        8. Quit when `q` is pressed.
        9. Always release the camera and destroy OpenCV windows.
    """
    args = parse_args()

    output_dir = prepare_output_dir()
    next_image_index = 1
    last_saved_index = 0

    cap = open_camera(args.camera_index, args.driver)
    try:
        set_resolution(
            cap,
            args.pixels_width,
            args.pixels_height,
        )

        display_width = args.display_width
        display_height = args.display_height

        fsm = FSM(CaptureState.VIDEO)
        freeze_frame = None
        freeze_saved = False

        while True:
            previous_state = fsm.state
            key = read_inputs()

            if key == ord("q"):
                break

            if fsm.state == CaptureState.FREEZE and key == ord("s"):
                if freeze_frame is not None and not freeze_saved:
                    save_freeze_frame(freeze_frame, output_dir, next_image_index)
                    last_saved_index = next_image_index
                    next_image_index += 1
                    freeze_saved = True
                    freeze_frame = None
                    fsm.update(CaptureState.VIDEO)
            else:
                apply_transitions(fsm, key)

            if previous_state != fsm.state:
                if fsm.state == CaptureState.FREEZE:
                    freeze_saved = False
                elif fsm.state == CaptureState.VIDEO:
                    freeze_frame = None
                    freeze_saved = False

            frame_to_display, freeze_frame = apply_actions(
                fsm=fsm,
                cap=cap,
                freeze_frame=freeze_frame,
                rotate=args.rotate,
                flip_x=args.flip_x,
                flip_y=args.flip_y,
                display_width=display_width,
                display_height=display_height,
            )

            label_geometry = _compute_last_saved_label_geometry(frame_to_display, last_saved_index)

            if fsm.state == CaptureState.FREEZE:
                frame_to_display = _apply_freeze_overlay(
                    frame=frame_to_display,
                    text_rect_top_left=label_geometry["rect_top_left"],
                    text_rect_bottom_right=label_geometry["rect_bottom_right"],
                    alpha=0.3,
                )

            frame_to_display = _draw_last_saved_index(frame_to_display, last_saved_index)
            cv2.imshow("capture_frames", frame_to_display)

    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()