import cv2
import csv
import time
from ultralytics import YOLO
from day103 import Sort
from day104b import DeepSort
from day104 import ApperanceEmbedder
from day102c import BidirectionalCounterV2

MIN_CONFIDENCE = 0.5
LINE_Y = 460
PERSON_CLASS_ID = 0

def run_accuracy_test(tracker_name, tracker, embedder, ground_truth_in, ground_truth_out, duration_seconds=30):
    """
    ground_truth_in / ground_truth_out: the number of crossings YOU know actually
    happened, decided and counted by you before running, not guessed afterward.
    This is what makes it a real accuracy test rather than another unverified run.
    """
    model = YOLO("yolov8n.pt")
    cap = cv2.VideoCapture(0)
    counter = BidirectionalCounterV2(line_y=LINE_Y, release_distance=100)

    log_filename = f"day105_accuracy_{tracker_name}_{int(time.time())}.csv"
    log_file = open(log_filename, "w", newline="")
    writer = csv.writer(log_file)
    writer.writerow(["frame_number", "track_id", "cy", "event"])

    frame_number = 0
    known_ids = set()
    start_time = time.time()

    while time.time() - start_time < duration_seconds:
        ret, frame = cap.read()
        if not ret:
            break
        frame_number += 1

        results = model(frame, verbose=False)
        result = results[0]

        detections = []
        embeddings = [] if embedder else None
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            if class_id != PERSON_CLASS_ID or confidence < MIN_CONFIDENCE:
                continue
            x1, y1, x2, y2 = map(int,box.xyxy[0])
            detections.append((x1,y1, x2, y2))
            if embedder:
                embeddings.append(embedder.get_embedding(frame, (x1, y1, x2, y2)))

        tracked = tracker.update(detections, embeddings) if embedder else tracker.update(detections)

        tracked_objects = {}
        for object_id, box in tracked:
            x1, y1, x2, y2 = box
            cx = int((x1 + x2) / 2)
            cy = int(y2)
            tracked_objects[object_id] = (cx, cy)
            event = "NEW" if object_id not in known_ids else "UPDATE"
            known_ids.add(object_id)
            writer.writerow([frame_number, object_id, cy, event])

        in_count, out_count, net = counter.update(tracked_objects)

        for object_id, box in tracked:
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"ID {object_id}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.line(frame, (0, LINE_Y), (frame.shape[1], LINE_Y), (255, 0, 0), 2)
        cv2.putText(frame, f"IN: {in_count} OUT: {out_count}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        cv2.imshow(f"Accuracy Test: {tracker_name}", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    log_file.close()
    cap.release()
    cv2.destroyAllWindows()

    in_error = abs(in_count - ground_truth_in)
    out_error = abs(out_count - ground_truth_out)

    print(f"\n--- {tracker_name} accuracy ---")
    print(f"Ground truth:  IN={ground_truth_in}, OUT={ground_truth_out}")
    print(f"Reported:      IN={in_count}, OUT={out_count}")
    print(f"Error:         IN off by {in_error}, OUT off by {out_error}")
    print(f"Log: {log_filename}")

    return in_error, out_error

if __name__ == "__main__":
    GROUND_TRUTH_IN = 3
    GROUND_TRUTH_OUT = 3

    print(f"Planned: {GROUND_TRUTH_IN} IN, {GROUND_TRUTH_OUT} OUT. Perform this EXACT sequence for SORT test.")
    input("Press Enter when ready...")
    sort_tracker = Sort(max_age=15, min_hits=3, iou_threshold=0.2)
    sort_in_err, sort_out_err = run_accuracy_test("SORT", sort_tracker, embedder=None,
                                                  ground_truth_in=GROUND_TRUTH_IN,
                                                  ground_truth_out=GROUND_TRUTH_OUT)

    print(f"\nNow repeat the EXACT SAME sequence for Deep SORT test.")
    input("Press Enter when ready...")
    embedder = ApperanceEmbedder()
    deepsort_tracker = DeepSort(max_age=15, min_hits=3, iou_threshold=0.2, appearance_weight=0.5)
    ds_in_err, ds_out_err = run_accuracy_test("DeepSORT", deepsort_tracker, embedder=embedder,
                                              ground_truth_in=GROUND_TRUTH_IN,
                                              ground_truth_out=GROUND_TRUTH_OUT)
    print(f"\n=== ACCURACY COMPARISON ===")
    print(f"SORT total error:      {sort_in_err + sort_out_err}")
    print(f"Deep SORT total error: {ds_in_err + ds_out_err}")