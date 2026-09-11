import cv2
import csv
import time
from ultralytics import YOLO
from day103 import Sort

MIN_CONFIDENCE = 0.5
LINE_Y = 460
PERSON_CLASS_ID = 0

def run_diagnostic_crowd_test(duration_seconds=30):
    model = YOLO("yolov8n.pt")
    tracker = Sort(max_age=15, min_hits=3, iou_threshold=0.2)
    cap = cv2.VideoCapture(0)

    log_filename = f"day106_diagnostic_{int(time.time())}.csv"
    log_file = open(log_filename, "w", newline="")
    writer = csv.writer(log_file)
    writer.writerow(["frame_number", "track_id", "cx", "cy", "event"])

    frame_number = 0
    known_ids = set()
    prev_positions = {}
    prev_in_registered_ids = set()
    in_count = 0

    print(f"Running for {duration_seconds}s - perform the same 4-person close crossing...")
    start_time = time.time()

    while time.time() - start_time < duration_seconds:
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

        for object_id, box in tracked:
            x1, y1, x2, y2 = box
            cx = int((x1 + x2) / 2)
            cy = int(y2)

            event = "NEW" if object_id not in known_ids else "UPDATE"
            known_ids.add(object_id)
            writer.writerow([frame_number, object_id, cx, cy, event])

            if object_id in prev_positions:
                prev_cy = prev_positions[object_id]
                if prev_cy < LINE_Y <= cy:
                    already_counted = object_id in prev_in_registered_ids
                    in_count += 1
                    prev_in_registered_ids.add(object_id)
                    writer.writerow([frame_number, "CROSSING", cx, cy,
                                     f"IN #{in_count} by ID {object_id}"
                                     + (" [ID ALREADY CROSSED BEFORE]" if already_counted else " [first crossing for this ID]")])

            prev_positions[object_id] = cy

        for object_id, box in tracked:
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"ID {object_id}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.line(frame, (0, LINE_Y), (frame.shape[1], LINE_Y), (255, 0, 0), 2)
        cv2.imshow("Diagnistic Crowd Test", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    log_file.close()
    cap.release()
    cv2.destroyAllWindows()
    print(f"\nTotal unique IDs seen: {len(known_ids)}")
    print(f"Total IN crossing logged:  {in_count}")
    print(f"Log saved to {log_filename}")

if __name__ == "__main__":
    run_diagnostic_crowd_test()