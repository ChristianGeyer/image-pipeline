import cv2

CAM_INDEX = 0  # try 0, 1, 2 if you have multiple cameras

cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_AVFOUNDATION)  # AVFoundation is macOS native

if not cap.isOpened():
    raise RuntimeError(f"Could not open camera index {CAM_INDEX}")

# Optional: request a size (not always honored)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("Backend:", cap.getBackendName())
print("Press 'q' to quit.")

count = 0
while True:
    ok, frame = cap.read()
    if not ok:
        count+=1
        if count >= 100:
            break
        print("Failed to read frame.")
        continue


    cv2.imshow("Camera Preview", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
