import numpy as np
from scipy.optimize import linear_sum_assignment
from filterpy.kalman import KalmanFilter

def box_to_state(bbox):
    x1, y1, x2, y2 = bbox
    w = x2 - x1
    h = y2 - y1
    cx = x1 + w / 2.0
    cy = y1 + h / 2.0
    s = w * h
    r = w / float(h)
    return np.array([cx, cy, s, r]).reshape((4, 1))

def state_to_box(state):
    cx, cy, s, r = state[0], state[1], state[2], state[3]
    w = np.sqrt(s * r)
    h = s / w
    return np.array([cx - w / 2.0, cy - h / 2.0, cx + w / 2.0, cy + h / 2.0]).flatten()

def iou(box_a, box_b):
    xx1 = max(box_a[0], box_b[0])
    yy1 = max(box_a[1], box_b[1])
    xx2 = min(box_a[2], box_b[2])
    yy2 = min(box_a[3], box_b[3])
    w = max(0.0, xx2 - xx1)
    h = max(0.0, yy2 - yy1)
    intersection = w * h
    area_a = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    area_b = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
    union = area_a + area_b - intersection
    return intersection / union if union > 0 else 0.0

class KalmanBoxTracker:
    count = 0

    def __init__(self, bbox):
        self.kf = KalmanFilter(dim_x=7, dim_z=4)
        self.kf.F = np.array([
            [1, 0, 0, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 1, 0],
            [0, 0, 1, 0, 0, 0, 1],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 1],
        ])

        self.kf.H = np.array([
            [1, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
        ])

        self.kf.R[2:, 2:] *= 10.0
        self.kf.P[4:, 4:] *= 1000.0
        self.kf.P *= 10.0
        self.kf.Q[-1, -1] *= 0.01
        self.kf.Q[4:, 4:] *= 0.01

        self.kf.x[:4] = box_to_state(bbox)

        self.id = KalmanBoxTracker.count
        KalmanBoxTracker.count += 1
        self.time_since_update = 0
        self.hits = 0
        self.hit_streak = 0

    def predict(self):
        if (self.kf.x[6] + self.kf.x[2]) <= 0:
            self.kf.x[6] *= 0.0
        self.kf.predict()
        self.time_since_update += 1
        return state_to_box(self.kf.x)

    def update(self, bbox):
        self.time_since_update = 0
        self.hits += 1
        self.hit_streak += 1
        self.kf.update(box_to_state(bbox))

    def get_state(self):
        return state_to_box(self.kf.x)

class Sort:
    def __init__(self, max_age=15, min_hits=3, iou_threshold=0.3):
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.trackers = []

    def update(self, detections):
        predicted_boxes = []

        for tracker in self.trackers:
            predicted_boxes.append(tracker.predict())

        if len(self.trackers) > 0 and len(detections) > 0:
            iou_matrix = np.zeros((len(detections), len(self.trackers)), dtype=np.float32)
            for d, det in enumerate(detections):
                for t, pred in enumerate(predicted_boxes):
                    iou_matrix[d, t] = iou(det, pred)

            row_ind, col_ind = linear_sum_assignment(-iou_matrix)
            matched_indices = np.array(list(zip(row_ind, col_ind)))

        else:
            matched_indices = np.empty((0, 2), dtype=int)

        unmatched_detections = [d for d in range(len(detections))
                                if d not in matched_indices[:, 0]]
        unmatched_trackers = [t for t in range(len(self.trackers))
                              if t not in matched_indices[:, 1]]

        matches = []
        for d, t in matched_indices:
            if iou_matrix[d, t] < self.iou_threshold:
                unmatched_detections.append(d)
                unmatched_trackers.append(t)

            else:
                matches.append((d, t))

        for d, t in matches:
            self.trackers[t].update(detections[d])

        for d in unmatched_detections:
            self.trackers.append(KalmanBoxTracker(detections[d]))

        self.trackers = [t for t in self.trackers if t.time_since_update <= self.max_age]

        results = []
        for t in self.trackers:
            if t.hit_streak >= self.min_hits or t.hits >= self.min_hits:
                box = t.get_state()
                results.append((t.id, box))
        return results

box_a = (100, 100, 200, 200)
box_b = (110, 110, 210, 210)
box_c = (195, 100, 295, 200)
box_d = (500, 500, 600, 600)

print("Heavy overlap:", iou(box_a, box_b))
print("Barely touching:", iou(box_a, box_c))
print("Zero overlap:", iou(box_a, box_d))

    