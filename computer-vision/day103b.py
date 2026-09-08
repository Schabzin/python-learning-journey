import cv2
from ultralytics import YOLO
from day103 import Sort
from day102c import BidirectionalCounterV2

MIN_CONFIDENCE = 0.5
LINE_Y = 240
PERSON_CLASS_ID = 0

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(0)
tracker = Sort(max_age=15, min_hits=3, iou_threshold=0.2)
counter = BidirectionalCounterV2(line_y=LINE_Y, release_distance=100)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, verbose=False)
    result = results[0]

    detections = []
    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        if class_id != PERSON_CLASS_ID or confidence < MIN_CONFIDENCE:
            continue
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        detections.append((x1, y1, x2, y2))

    tracked = tracker.update(detections)
    print(f"Active tracks this frame: {len(tracked)} - IDs: {[t[0] for t in tracked]}")
    tracked_objects = {}

    for object_id, box in tracked:
        x1, y1, x2, y2 = box
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)
        tracked_objects[object_id] = (cx, cy)

    in_count, out_count, net = counter.update(tracked_objects)

    for object_id, box in tracked:
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"ID {object_id}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.line(frame, (0, LINE_Y), (frame.shape[1], LINE_Y), (255, 0, 0), 2)
    cv2.putText(frame, f"IN: {in_count} OUT: {out_count} NET: {net}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    cv2.imshow("SORT Passenger Counter", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()