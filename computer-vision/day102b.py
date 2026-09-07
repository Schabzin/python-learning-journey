import cv2
from ultralytics import YOLO
from day101 import CentroidTracker
from day101c import BidirectionalCounter

MIN_CONFIDENCE = 0.5
LINE_Y = 240
PERSON_CLASS_ID = 0

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(0)
tracker = CentroidTracker(max_disappeared=20, max_distance=150)
counter = BidirectionalCounter(line_y=LINE_Y)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, verbose=False)
    result = results[0]

    boxes = []
    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])

        if class_id != PERSON_CLASS_ID or confidence < MIN_CONFIDENCE:
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        boxes.append((x1, y1, x2 - x1, y2 - y1))

    tracked_objects = tracker.update(boxes)
    in_count, out_count, net = counter.update(tracked_objects)

    for object_id, centroid in tracked_objects.items():
        cv2.putText(frame, f"ID {object_id}", (centroid[0] - 10, centroid[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.circle(frame, centroid, 4, (0, 0, 255), -1)

    cv2.line(frame, (0, LINE_Y), (frame.shape[1], LINE_Y), (255, 0, 0), 2)
    cv2.putText(frame, f"IN: {in_count} OUT: {out_count} NET: {net}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    cv2.imshow("YOLO Passenger Counter", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
 