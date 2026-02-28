import cv2
import numpy as np
import platform

def open_camera(camera_id):
    sys = platform.system()
    if sys == "Darwin": # mac
        cap = cv2.VideoCapture(camera_id, cv2.CAP_AVFOUNDATION)
    elif sys == "Windows": # windows
        cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(camera_id, 0) # default backend
    if not cap.isOpened():
        raise RuntimeError("could not open camera.")
    return cap, sys

def rotate_frame(frame, rotation_deg):
    if rotation_deg == 90:
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    elif rotation_deg == 180:
        frame = cv2.rotate(frame, cv2.ROTATE_180)
    elif rotation_deg == 270:
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return frame

def flip_frame(frame, mirror_x, mirror_y):
    if mirror_x and (not mirror_y):
        frame = cv2.flip(frame, 1)
    elif (not mirror_x) and mirror_y:
        frame = cv2.flip(frame, 0)
    elif mirror_x and mirror_y:
        frame = cv2.flip(frame, -1)
    return frame

def downsampled_dimensions(w, h, downsample_factor, rotation_deg):
    w_downsampled = w//downsample_factor
    h_downsampled = h//downsample_factor
    if rotation_deg in (90, 270):
        w_downsampled, h_downsampled = h_downsampled, w_downsampled
    return int(w_downsampled), int(h_downsampled)

def main():
    # open camera
    cap, sys = open_camera(0)
    print(f"opened camera, detected system {sys}")
    # set resolution
    w_request = 4656
    h_request = 3496
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w_request)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h_request)
    w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"requested resolution {w_request}x{h_request}, got {w}x{h}.")
    # display downsample
    downsample_factor = 4
    # mirror axis
    x_mirrored = True # depends on camera orientation
    y_mirrored = True # depends on camera orientation
    mirror_x = False # True for selfie mode
    mirror_y = False # True if upside down desired
    if mirror_x:
        print(f"selfie mode (mirroring x axis).")
    else:
        print(f"normal mode (not mirroring x axis).")
    mirror_x = x_mirrored ^ mirror_x
    mirror_y = y_mirrored ^ mirror_y
    # rotation
    rotation_deg = 90
    print(f"rotating by {rotation_deg} degrees clockwise.")
    # downsampled dimensions
    w_display, h_display = downsampled_dimensions(w, h, downsample_factor, rotation_deg)
    print(f"downsampled to {w_display}x{h_display}.")


    while True:
        ret, frame = cap.read()
        if not ret:
            print("could not read frame.")
            break
        # rotate frame
        frame = rotate_frame(frame, rotation_deg)
        # flip frame
        #frame = cv2.flip(frame, -1)
        frame = flip_frame(frame, mirror_x, mirror_y)
        # downsample frame
        frame_display = cv2.resize(frame, (w_display, h_display))
        # display frame
        cv2.imshow("frame_display", frame_display)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()