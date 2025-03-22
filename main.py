import cv2

from detection import ProcessImage
from keyboard import KeyPress

cam = cv2.VideoCapture(0)
skip_process = False
while cam.isOpened():
    success, image = cam.read()
    if not success: continue

    image, pressed = ProcessImage(image, not skip_process)
    for key in pressed:
        KeyPress(key)

    cv2.imshow('AR Keyboard', image)
    if cv2.waitKey(5) & 0xFF == ord('~'): break

    skip_process = not skip_process

cam.release()