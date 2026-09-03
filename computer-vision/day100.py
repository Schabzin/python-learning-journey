import cv2
import numpy as np

image = cv2.imread("test_photo.jpg.jpg")
height, width, channels = image.shape
print(f"Image is {width}px wide, {height}px tall, {channels} color channels")
print(f"Pixel at (0,0) - Blue: {image[0, 0, 0]}, Green: {image[0, 0, 1]}, Red: {image[0, 0, 2]}")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
print(f"Grayscale image shape: {gray.shape}")
cv2.imwrite("test_photo_gray.jpg", gray)

top = height // 3
bottom = (height // 3) * 2
left = width // 3
right = (width // 3) * 2

cropped_door_area = image[top:bottom, left:right]
cv2.imwrite("cropped_test.jpg", cropped_door_area)
resized = cv2.resize(image, (640, 640))
print(f"Resized shape: {resized.shape}")
resized_correctly = cv2.resize(image, (640, 640), interpolation=cv2.INTER_AREA)

wrong_bright = image + 100
print(f"Original pixel value: {image[0,0,0]}")
print(f"After image + 100 (WRONG, can overflow): {wrong_bright[0,0,0]}")
correct_bright = cv2.add(image, np.full(image.shape, 100, dtype=np.uint8))
print(f"After cv2.add (correct, saturates at 255): {correct_bright[0,0,0]}")
cv2.imwrite("wrong_bright.jpg", wrong_bright)
cv2.imwrite("correct_bright.jpg", correct_bright)

capture = cv2.VideoCapture(0)

if not capture.isOpened():
    raise RuntimeError("Could not open camera - check it's connected and not in use by another program")

frame_count = 0
while True:
    success, frame = capture.read()

    if not success:
        print("Failed to read frame - stopping")
        break

    frame_count += 1
    if frame_count % 5 == 0:
        cv2.imwrite(f"frame_{frame_count}.jpg", frame)
        print(f"Saved frame {frame_count}")

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

capture.release()
cv2.destroyAllWindows()
print(f"Stopped after {frame_count} frames")