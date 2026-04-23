from grove.gpio import GPIO
import time
import cv2
import sys
import numpy as np
import re

from FaceReg.face_recog5 import initialize_recognizer
from FaceReg.face_recog5 import recognize_video

face_r = initialize_recognizer()


pir = GPIO(5, GPIO.IN)  # D5-portti

while True:
    if pir.read():
        print("Liiketta havaittu!")
        recognize_video(face_r)
    time.sleep(1)
