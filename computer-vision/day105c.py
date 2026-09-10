import cv2
import time
from ultralytics import YOLO
from day104b import DeepSort
from day104 import ApperanceEmbedder
from day102c import BidirectionalCounterV2
from day105b import run_accuracy_test

MIN_CONFIDENCE = 0.5
LINE_Y = 460
PERSON_CLASS_ID = 0

if __name__ == "__main__":
    GROUND_TRUTH_IN = 3
    GROUND_TRUTH_OUT = 3

    weights_to_test = [0.2, 0.0]

    for weight in weights_to_test:
        print(f"\n\n=== Testing appearance_weight={weight} ===")
        print(f"Perform the SAME 3-person sequence as before: {GROUND_TRUTH_IN} IN, {GROUND_TRUTH_OUT} OUT")
        input("Press Enter when ready...")

        embedder = ApperanceEmbedder()
        tracker = DeepSort(max_age=15, min_hits=3, iou_threshold=0.2, appearance_weight=weight)
        in_err, out_err = run_accuracy_test(f"DeepSORT_weight{weight}", tracker, embedder=embedder,
                                            ground_truth_in=GROUND_TRUTH_IN,
                                            ground_truth_out=GROUND_TRUTH_OUT)
        print(f"appearance_weight={weight} total error: {in_err + out_err}")