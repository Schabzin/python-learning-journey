import cv2
import numpy as np
from scipy.optimize import linear_sum_assignment
from ultralytics import YOLO
from day103 import KalmanBoxTracker, iou
from day104 import ApperanceEmbedder, cosine_distance
from day102c import BidirectionalCounterV2

class DeepSortTracker(KalmanBoxTracker):
    def __init__(self, bbox, embedding):
        super().__init__(bbox)
        self.embedding = embedding

    def update_embedding(self, new_embedding, alpha=0.7):
        self.embedding = alpha * self.embedding + (1 - alpha) * new_embedding

class DeepSort:
    def __init__(self, max_age=15, min_hits=3, iou_threshold=0.2,
                 appearance_weight=0.5, max_appearance_distance=0.5):
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold

        self.appearance_weight = appearance_weight
        self.max_appearance_distance = max_appearance_distance
        self.trackers = []

    def update(self, detections, embeddings):
        predicted_boxes = [t.predict() for t in self.trackers]

        if len(self.trackers) > 0 and len(detections) > 0:
            iou_matrix = np.zeros((len(detections), len(self.trackers)), dtype=np.float32)
            appearance_matrix = np.zeros((len(detections), len(self.trackers)), dtype=np.float32)

            for d, det in enumerate(detections):
                for t, pred in enumerate(predicted_boxes):
                    iou_matrix[d, t] = iou(det, pred)
                    appearance_matrix[d, t] = cosine_distance(embeddings[d], self.trackers[t].embedding)

            motion_cost = 1.0 - iou_matrix
            combined_cost = ((1 - self.appearance_weight) * motion_cost +
                             self.appearance_weight * appearance_matrix)

            row_ind, col_ind = linear_sum_assignment(combined_cost)
            matched_indices = np.array(list(zip(row_ind, col_ind)))
        else:
            iou_matrix = np.zeros((len(detections), len(self.trackers)))
            appearance_matrix = np.zeros((len(detections), len(self.trackers)))
            matched_indices = np.empty((0, 2), dtype=int)

        unmatched_detections = [d for d in range(len(detections)) if d not in matched_indices[:, 0]]
        unmatched_trackers = [t for t in range(len(self.trackers)) if t not in matched_indices[:, 1]]

        matches = []
        for d, t in matched_indices:
            if iou_matrix[d, t] < self.iou_threshold or appearance_matrix[d, t] > self.max_appearance_distance:
                unmatched_detections.append(d)
                unmatched_trackers.append(t)
            else:
                matches.append((d, t))

        for d, t in matches:
            self.trackers[t].update(detections[d])
            self.trackers[t].update_embedding(embeddings[d])

        for d in unmatched_detections:
            self.trackers.append(DeepSortTracker(detections[d], embeddings[d]))

        self.trackers = [t for t in self.trackers if t.time_since_update <= self.max_age]

        results = []
        for t in self.trackers:
            if t.hit_streak >= self.min_hits or t.hits >= self.min_hits:
                results.append((t.id, t.get_state()))
        return results

if __name__ == "__main__":
    MIN_CONFIDENCE = 0.5
    LINE_Y = 460
    PERSON_CLASS_ID = 0

    model = YOLO("yolov8n.pt")
    embedder = ApperanceEmbedder()
    cap = cv2.VideoCapture(0)
    tracker = DeepSort(max_age=15, min_hits=3, iou_threshold=0.2, appearance_weight=0.5)
    counter = BidirectionalCounterV2(line_y=LINE_Y, release_distance=100)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

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
            embeddings.append(embedder.get_embedding(frame, (x1, y1, x2, y2)))

        tracked = tracker.update(detections, embeddings)
        print(f"Frame IDs: {[t[0] for t in tracked]}")

        tracked_objects = {}
        for object_id, box in tracked:
            x1, y1, x2, y2 = box
            cx = int((x1 + x2) / 2)
            cy = int(y2)
            print(f"ID {object_id}: cy={cy}, line={LINE_Y}")
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

        cv2.imshow("Deep SORT Passenger Counter", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

            