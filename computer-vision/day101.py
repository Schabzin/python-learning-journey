from collections import OrderedDict
from scipy.spatial import distance as dist
import numpy as np
import cv2

class CentroidTracker:
    def __init__(self, max_disappeared=20, max_distance=75):
        self.next_object_id = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance

    def register(self, centroid):
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1

    def deregister(self, object_id):
        del self.objects[object_id]
        del self.disappeared[object_id]

    def update(self, bounding_boxes):
        if len(bounding_boxes) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.objects

        input_centroids = np.zeros((len(bounding_boxes), 2), dtype="int")
        for i, (x, y, w, h) in enumerate(bounding_boxes):
            cx = int(x + (w / 2.0))
            cy = int(y + (h / 2.0))
            input_centroids[i] = (cx, cy)

        if len(self.objects) == 0:
            for centroid in input_centroids:
                self.register(centroid)

        else:
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())

            D = dist.cdist(np.array(object_centroids), input_centroids)
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            used_rows = set()
            used_cols = set()

            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue
                if D[row, col] > self.max_distance:
                    continue

                object_id = object_ids[row]
                self.objects[object_id] = input_centroids[col]
                self.disappeared[object_id] = 0

                used_rows.add(row)
                used_cols.add(col)

            unused_rows = set(range(D.shape[0])) - used_rows
            unused_cols = set(range(D.shape[1])) - used_cols

            for row in unused_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)

            for col in unused_cols:
                self.register(input_centroids[col])

        return self.objects

if __name__ == "__main__":
    MIN_CONTOUR_AREA = 3000
    cap = cv2.VideoCapture(0)
    back_sub = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
    tracker = CentroidTracker(max_disappeared=20, max_distance=75)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        fg_mask = back_sub.apply(frame)
        _, thresh = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
        clean_mask = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(clean_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        boxes = []
        for c in contours:
            if cv2.contourArea(c) < MIN_CONTOUR_AREA:
                continue
            boxes.append(cv2.boundingRect(c))

        tracked_objects = tracker.update(boxes)

        for (x, y, w, h) in boxes:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        for object_id, centroid in tracked_objects.items():
            text = f"ID {object_id}"
            cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 0, 255), -1)

        cv2.imshow("Centroid Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
