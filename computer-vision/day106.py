import cv2
import time
from ultralytics import YOLO
from day103 import Sort
from day105b import run_accuracy_test

MIN_CONFIDENCE = 0.5
LINE_Y = 460
PERSON_CLASS_ID = 0

def run_crossing_close_together_test(ground_truth_in, ground_truth_out, duration_seconds=30):
    """
    A variant specifically for testing CLOSE, OVERLAPPING crossing -
    multiple people passing through the line within the same 1-2 frames,
    not staggered. This is closer to real taxi-door crowding than people
    taking turns, and is where identity-swap errors are most likely.
    """
    model = YOLO("yolov8n.pt")
    tracker = Sort(max_age=15, min_hits=3, iou_threshold=0.2)
    return run_accuracy_test("SORT_high_density", tracker, embedder=None,
                             ground_truth_in=ground_truth_in,
                             ground_truth_out=ground_truth_out,
                             duration_seconds=duration_seconds)

if __name__ == "__main__":
    print("Day 106: High-density SORT validation")
    print("Gather as many peopl as you can (aim for 4+). If unavailable,")
    print("use fewer people but have them cross AS CLOSE TOGETHER as possible -")
    print("overlapping, not one at a time - to stress-test identity matching.\n")

    GROUND_TRUTH_IN = 4
    GROUND_TRUTH_OUT = 4

    print(f"Planned: {GROUND_TRUTH_IN} people cross down together (close/overlapping), "
          f"then all {GROUND_TRUTH_OUT} cross back up together.")
    input("Press Enter when ready...")

    in_err, out_err = run_crossing_close_together_test(GROUND_TRUTH_IN, GROUND_TRUTH_OUT)

    print(f"\n=== HIGH-DENSITY RESULT ===")
    print(f"Total error: {in_err + out_err}")
    print(f"Compared against Day 105's 3-person SORT result (error 4) and Deep SORT's (error 5)")