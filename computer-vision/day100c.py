import cv2

capture = cv2.VideoCapture(0)

if not capture.isOpened():
    raise RuntimeError("Could not open camera")

background_subtractor = cv2.createBackgroundSubtractorMOG2(
    history=500, varThreshold=16, detectShadows=True
)

frame_count = 0
while True:
    success, frame = capture.read()
    if not success:
        print("Failed to read - stopping")
        break

    frame_count += 1
    foreground_mask = background_subtractor.apply(frame)

    if frame_count < 30:
        cv2.putText(frame, "Calibrating background...", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    else:
        true_foreground = cv2.threshold(foreground_mask, 200, 255, cv2.THRESH_BINARY)[1]
        motion_area = cv2.countNonZero(true_foreground)

        if motion_area > 5000:
            cv2.putText(frame, "Motion in frame", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow("Live Feed", frame)
    cv2.imshow("Foreground Mask", foreground_mask)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

capture.release()
cv2.destroyAllWindows()