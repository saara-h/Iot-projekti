import time
import cv2
from grove.gpio import GPIO
paused=False
pir= GPIO(5, GPIO.IN)
while True:
    if cv2.waitKey(1) & 0xFF == ord('q'):
        paused=not paused
        print(paused)
    if paused:
        print("paused")
    elif pir.read():
        print("motion")
    else:
        print("no motion")
    time.sleep(1)


