"""
Public API for the `camera` package.

Import public camera utilities from here, not from submodules.

Exports:
    open_camera
    set_resolution
    read_frame
    rotate_frame
    flip_frame
    resize_frame
"""

from .camera import (
    open_camera,
    set_resolution,
    read_frame,
    rotate_frame,
    flip_frame,
    resize_frame,
)

__all__ = [
    "open_camera",
    "set_resolution",
    "read_frame",
    "rotate_frame",
    "flip_frame",
    "resize_frame",
]