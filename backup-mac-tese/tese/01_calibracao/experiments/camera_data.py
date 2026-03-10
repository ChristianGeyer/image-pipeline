import cv2
import subprocess
import json
import re

CAM_INDEX = 0  # try 0,1,2...

def fourcc_to_str(v: int) -> str:
    return "".join([chr((v >> 8*i) & 0xFF) for i in range(4)])

def dump_opencv_props(index: int):
    cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
    if not cap.isOpened():
        print(f"[OpenCV] Could not open camera index {index}")
        return

    props = {
        "backend": cap.getBackendName() if hasattr(cap, "getBackendName") else "unknown",
        "frame_width": cap.get(cv2.CAP_PROP_FRAME_WIDTH),
        "frame_height": cap.get(cv2.CAP_PROP_FRAME_HEIGHT),
        "fps": cap.get(cv2.CAP_PROP_FPS),
        "format": cap.get(cv2.CAP_PROP_FORMAT),
        "fourcc_int": cap.get(cv2.CAP_PROP_FOURCC),
        "brightness": cap.get(cv2.CAP_PROP_BRIGHTNESS),
        "contrast": cap.get(cv2.CAP_PROP_CONTRAST),
        "saturation": cap.get(cv2.CAP_PROP_SATURATION),
        "hue": cap.get(cv2.CAP_PROP_HUE),
        "gain": cap.get(cv2.CAP_PROP_GAIN),
        "exposure": cap.get(cv2.CAP_PROP_EXPOSURE),
        "auto_exposure": cap.get(cv2.CAP_PROP_AUTO_EXPOSURE),
        "auto_wb": cap.get(cv2.CAP_PROP_AUTO_WB),
        "wb_temp": cap.get(cv2.CAP_PROP_WB_TEMPERATURE),
    }

    fourcc = int(props["fourcc_int"])
    props["fourcc_str"] = fourcc_to_str(fourcc)

    cap.release()

    print("\n=== OpenCV-reported properties ===")
    for k, v in props.items():
        # OpenCV returns 0.0 or -1.0 for many unsupported properties
        print(f"{k:>15}: {v}")

def list_usb_devices_system_profiler():
    print("\n=== macOS USB device list (system_profiler) ===")
    try:
        # JSON output is easiest to parse
        out = subprocess.check_output(
            ["system_profiler", "SPUSBDataType", "-json"],
            text=True
        )
        data = json.loads(out)

        # The structure is nested; we walk it and print entries that look like cameras.
        def walk(items):
            for it in items:
                # each item may have nested children
                name = it.get("_name", "")
                vendor = it.get("vendor_id", "")
                product = it.get("product_id", "")
                manufacturer = it.get("manufacturer", "")
                serial = it.get("serial_num", "")

                # Heuristic: print anything with "Camera", "UVC", "Webcam", etc.
                if re.search(r"(camera|uvc|webcam|video)", name, re.IGNORECASE):
                    print(f"- Name: {name}")
                    if manufacturer: print(f"  Manufacturer: {manufacturer}")
                    if vendor:       print(f"  Vendor ID: {vendor}")
                    if product:      print(f"  Product ID: {product}")
                    if serial:       print(f"  Serial: {serial}")
                    print()

                children = it.get("_items", [])
                if children:
                    walk(children)

        top = data.get("SPUSBDataType", [])
        walk(top)

        print("Tip: if nothing shows up, unplug/plug the camera and rerun.")

    except subprocess.CalledProcessError as e:
        print("system_profiler failed:", e)
    except json.JSONDecodeError:
        print("Could not parse system_profiler JSON output.")

if __name__ == "__main__":
    dump_opencv_props(CAM_INDEX)
    list_usb_devices_system_profiler()
