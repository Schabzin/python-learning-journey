import cv2


capture = cv2.VideoCapture(0)
if not capture.isOpened():
    raise RuntimeError("Could not open camera")

background_subtractor = cv2.createBackgroundSubtractorMOG2(
    history=500, varThreshold=16, detectShadows=True
)

MIN_CONTOUR_AREA = 3000

frame_count = 0
while True:
    success, frame = capture.read()
    if not success:
        print("Failed to read frame - stopping")
        break

    frame_count += 1
    foreground_mask = background_subtractor.apply(frame)

    if frame_count < 30:
        cv2.putText(frame, "Calibrating background...", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    else:
        true_foreground = cv2.threshold(foreground_mask, 200, 255, cv2.THRESH_BINARY)[1]

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        true_foreground = cv2.morphologyEx(true_foreground, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(true_foreground, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        real_object_count = 0

        for contour in contours:
            area = cv2.contourArea(contour)

            if area < MIN_CONTOUR_AREA:
                continue

            real_object_count += 1
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"Object ({int(area)}px)", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.putText(frame, f"Real objects: {real_object_count}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    cv2.imshow("Live Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

capture.release()
cv2.destroyAllWindows()

