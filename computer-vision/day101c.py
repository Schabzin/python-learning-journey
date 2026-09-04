import cv2
from day101 import CentroidTracker

class BidirectionalCounter:
    def __init__(self, line_y):
        self.line_y = line_y
        self.previous_positions = {}
        self.resolved_ids = set()

        self.in_count = 0
        self.out_count = 0

    @property
    def net_occupancy(self):
        return self.in_count - self.out_count

    def update(self, tracked_objects):
        for object_id, (cx, cy) in tracked_objects.items():
            if object_id in self.resolved_ids:
                self.previous_positions[object_id] = cy
                continue

            if object_id in self.previous_positions:
                prev_cy = self.previous_positions[object_id]

                if prev_cy < self.line_y <= cy:
                    self.in_count += 1
                    self.resolved_ids.add(object_id)

                elif prev_cy > self.line_y >= cy:
                    self.out_count += 1
                    self.resolved_ids.add(object_id)

            self.previous_positions[object_id] =cy

        return self.in_count, self.out_count, self.net_occupancy

if __name__ == "__main__":
    MIN_CONTOUR_AREA = 3000
    LINE_Y = 240

    cap = cv2.VideoCapture(0)
    back_sub = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
    tracker = CentroidTracker(max_disappeared=20, max_distance=75)
    counter = BidirectionalCounter(line_y=LINE_Y)
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
            print(f"Frame: {len(boxes)} box(es) - areas: {[cv2.contourArea(c) for c in contours if cv2.contourArea(c) >= MIN_CONTOUR_AREA]}")

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

        cv2.imshow("Bidirectional Passenger Counter", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
