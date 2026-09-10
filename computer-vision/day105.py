import cv2
import time
import csv
from ultralytics import YOLO
from day103 import Sort
from day104b import DeepSort
from day104 import ApperanceEmbedder

MIN_CONFIDENCE = 0.5
PERSON_CLASS_ID = 0

def run_benchmark(tracker_name, tracker, embedder, video_source, duration_seconds=20):
    """
    Runs one tracker against live video for a fixed duration, logging per-frame
    timing. Using a fixed TIME window (not frame count) means both trackers get
    a fair, equal-length real-world test, regardless of how fast either runs.
    """
    model = YOLO("yolov8n.pt")
    cap = cv2.VideoCapture(video_source)

    log_filename = f"day105_benchmark_{tracker_name}_{int(time.time())}.csv"
    log_file = open(log_filename, "w", newline="")
    writer = csv.writer(log_file)
    writer.writerow(["frame_number", "frame_time_ms", "detections_count", "tracks_count"])

    frame_number = 0
    start_time = time.time()

    while time.time() - start_time < duration_seconds:
        ret, frame = cap.read()
        if not ret:
            break
        frame_number += 1

        frame_start = time.time()

        results = model(frame, verbose=False)
        result = results[0]

        detections = []
        embeddings = []
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            if class_id != PERSON_CLASS_ID or confidence < MIN_CONFIDENCE:
                continue
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            detections.append((x1, y1, x2, y2))
            if embedder:
                embeddings.append(embedder.get_embedding(frame, (x1, y1, x2, y2)))

        if embedder:
            tracked = tracker.update(detections, embeddings)
        else:
            tracked = tracker.update(detections)

        frame_time_ms = (time.time() - frame_start) * 1000

        writer.writerow([frame_number, f"{frame_time_ms:.2f}", len(detections), len(tracked)])

        cv2.imshow(f"Benchmark: {tracker_name}", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    elapsed = time.time() - start_time
    fps = frame_number / elapsed if elapsed > 0 else 0

    log_file.close()
    cap.release()
    cv2.destroyAllWindows()

    print(f"\n--- {tracker_name} results ---")
    print(f"Frames processed: {frame_number} in {elapsed:.1f}s")
    print(f"Average FPS: {fps:.2f}")
    print(f"Log saved to {log_filename}")
    return fps

if __name__ == "__main__":
    print("Running SORT benchmark first - get in frame and move naturally for 20 seconds...")
    sort_tracker = Sort(max_age=15, min_hits=3, iou_threshold=0.2)
    sort_fps = run_benchmark("SORT", sort_tracker, embedder=None, video_source=0, duration_seconds=20)

    input("\nPress Enter when ready to run the Deep SORT benchmark (same test, same conditions)...")

    print("Running Deep SORT benchmark - same movement pattern if possible, for a fair comparison...")
    embedder = ApperanceEmbedder()
    deepsort_tracker = DeepSort(max_age=15, min_hits=3, iou_threshold=0.2, appearance_weight=0.5)
    deepsort_fps = run_benchmark("DeepSORT", deepsort_tracker, embedder=embedder, video_source=0, duration_seconds=20)

    print(f"\n=== FINAL COMPARISON ===")
    print(f"SORT:      {sort_fps:.2f} FPS")
    print(f"Deep SORT: {deepsort_fps:.2f} FPS")
    print(f"Deep SORT is {(sort_fps / deepsort_fps):.2f}x slower than SORT" if deepsort_fps > 0 else "Deep SORT failed t")
