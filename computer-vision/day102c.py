import cv2
from ultralytics import YOLO
from day101 import CentroidTracker

class BidirectionalCounterV2:
    def __init__(self, line_y, release_distance=100):
        self.line_y = line_y
        self.release_distance = release_distance

        self.previous_positions = {}
        self.eligible_ids = {}

        self.in_count = 0
        self.out_count = 0

    @property
    def net_occupancy(self):
        return self.in_count - self.out_count

    def update(self, tracked_objects):
        for object_id, (cx, cy) in tracked_objects.items():
            if object_id not in self.eligible_ids:
                self.eligible_ids[object_id] = True

            if object_id in self.previous_positions:
                prev_cy = self.previous_positions[object_id]

                if prev_cy < self.line_y <= cy and self.eligible_ids:
                    self.in_count += 1
                    self.eligible_ids[object_id] = False

                elif prev_cy > self.line_y >= cy and self.eligible_ids[object_id]:
                    self.out_count += 1
                    self.eligible_ids[object_id] = False

                if not self.eligible_ids[object_id]:
                    distance_from_line = abs(cy - self.line_y)
                    if distance_from_line > self.release_distance:
                        self.eligible_ids[object_id] = True

            self.previous_positions[object_id] = cy

        return self.in_count, self.out_count, self.net_occupancy

if __name__ == "__main__":
    MIN_CONFIDENCE = 0.5
    LINE_Y = 240
    PERSON_CLASS_ID = 0

    model = YOLO("yolov8n.pt")
    cap = cv2.VideoCapture(0)
    tracker = CentroidTracker(max_disappeared=20, max_distance=150)
    counter = BidirectionalCounterV2(line_y=LINE_Y, release_distance=100)

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

        for (x, y, w, h) in boxes:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        for object_id, centroid in tracked_objects.items():
            cv2.putText(frame, f"ID {object_id}", (centroid[0] - 10, centroid[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.circle(frame, centroid, 4, (0, 0, 255), -1)

        cv2.line(frame, (0, LINE_Y), (frame.shape[1], LINE_Y), (255, 0, 0), 2)
        cv2.putText(frame, f"IN: {in_count} OUT: {out_count} NET: {net}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        cv2.imshow("YOLO Passenger Counter v2", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()