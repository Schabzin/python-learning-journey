import cv2
import numpy as np

image = cv2.imread("test_photo.jpg")
annotated = image.copy()

top_left = (400, 300)
bottom_right = (900, 800)

green = (0, 255, 0)
thickness = 3

cv2.rectangle(annotated, top_left, bottom_right, green, thickness)

font = cv2.FONT_HERSHEY_SIMPLEX
label = "Passenger detected"
label_position = (400, 280)
font_scale = 0.8
cv2.putText(annotated, label, label_position, font, font_scale, green, 2)

cv2.imwrite("annotated_test.jpg", annotated)
print("Saved annotated_test.jpg - box + label drawn")

capture = cv2.VideoCapture(0)

if not capture.isOpened():
    raise RuntimeError("Could not open camera")
success, previous_frame = capture.read()
if not success:
    raise RuntimeError("Could not read initial frame")

previous_gray = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)

while True:
    success, current_frame = capture.read()
    if not success:
        print("Failed to read frame - stopping")
        break

    current_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(previous_gray, current_gray)
    _, motion_mask = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    motion_percentage = (np.count_nonzero(motion_mask) / motion_mask.size) * 100

    if motion_percentage > 2.0:
        print(f"Motion detected: {motion_percentage:.2f}% of frame changed")

    previous_gray = current_gray

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    
capture.release()
cv2.destroyAllWindows()