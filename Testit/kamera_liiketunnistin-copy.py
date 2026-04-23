from grove.gpio import GPIO
import time
import cv2
cap = cv2.VideoCapture(0)


pir = GPIO(5, GPIO.IN)  # D5-portti

while True:
    if pir.read():
        print("Liiketta havaittu!")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow("Webcam", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    time.sleep(1)
