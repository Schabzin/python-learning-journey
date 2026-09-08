import cv2
import csv
import time
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

log_filename = f"day103_log_{int(time.time())}.csv"
log_file = open(log_filename, "w", newline="")
log_writer = csv.writer(log_file)
log_writer.writerow(["frame_number", "track_id", "cx", "cy", "event"])

frame_number = 0
known_ids = set()
prev_in, prev_out = 0, 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame_number += 1

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

    tracked_objects = {}
    for object_id, box in tracked:
        x1, y1, x2, y2 = box
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)
        tracked_objects[object_id] = (cx, cy)

        event = "NEW" if object_id not in known_ids else "UPDATE"
        known_ids.add(object_id)
        log_writer.writerow([frame_number, object_id, cx, cy, event])

    in_count, out_count, net = counter.update(tracked_objects)

    if in_count != prev_in:
        log_writer.writerow([frame_number, "COUNT", "", "", f"IN increment to {in_count}"])
        prev_in = in_count
    if out_count != prev_out:
        log_writer.writerow([frame_number, "COUNT", "", "", f"OUT increment to {out_count}"])
        prev_out = out_count

    for object_id, box in tracked:
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"ID {object_id}", (x1, y1 -10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.line(frame, (0, LINE_Y), (frame.shape[1], LINE_Y), (255, 0, 0), 2)
    cv2.putText(frame, f"IN: {in_count} OUT: {out_count} NET: {net}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    cv2.imshow("SORT Diagnostic Logging", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

log_file.close()
cap.release()
cv2.destroyAllWindows()
print(f"Log saved to {log_filename}")