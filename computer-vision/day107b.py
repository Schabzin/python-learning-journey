import cv2
from ultralytics import YOLO
from day103 import Sort
from day108b import BidirectionalCounterV3
from day107 import create_passenger_tables, start_trip, log_crossing, end_trip

MIN_CONFIDENCE = 0.5
LINE_Y = 460
PERSON_CLASS_ID = 0
TAXI_ID = "TEST-VAN-01"

create_passenger_tables()

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(0)
tracker = Sort(max_age=15, min_hits=3, iou_threshold=0.2)
counter = BidirectionalCounterV3(line_y=LINE_Y, buffer_zone=15)

trip_id = start_trip(TAXI_ID)
print(f"Trip started, trip_id={trip_id}. Press 'q' to end the trip.")

prev_in, prev_out = 0, 0

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

    tracked_objects = {}
    for object_id, box in tracked:
        x1, y1, x2, y2 = box
        cx = int((x1 + x2) / 2)
        cy = int(y2)
        tracked_objects[object_id] = (cx, cy)

    in_count, out_count, net = counter.update(tracked_objects)
    print(f"cy tracking check - last crossing: {counter.last_crossing_direction} by ID {counter.last_crossing_id}, IN={in_count} OUT={out_count}")

    if counter.last_crossing_direction == "IN":
        log_crossing(trip_id, direction="IN", track_id=counter.last_crossing_id, running_net=net)
    elif counter.last_crossing_direction == "OUT":
        log_crossing(trip_id, direction="OUT", track_id=counter.last_crossing_id, running_net=net)

    for object_id, box in tracked:
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"ID {object_id}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.line(frame, (0, LINE_Y), (frame.shape[1], LINE_Y), (255, 0, 0), 2)
    cv2.putText(frame, f"IN: {in_count} OUT: {out_count} NET: {net}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    cv2.imshow("Live Pipeline with Persistence", frame)
    key = cv2.waitKey(1) & 0xFF
    window_closed = cv2.getWindowProperty("Live Pipeline with Persistence", cv2.WND_PROP_VISIBLE) < 1
    if key == ord('q') or window_closed:
        break

end_trip(trip_id, final_in=in_count, final_out=out_count, final_net=net)
print(f"Trip ended, trip_id={trip_id}. Final: IN={in_count}, OUT={out_count}, NET={net}")

cap.release()
cv2.destroyAllWindows()