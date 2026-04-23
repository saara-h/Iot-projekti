from grove.gpio import GPIO
import time

pir = GPIO(5, GPIO.IN)  # D5-portti

while True:
    if pir.read():
        print("Liiketta havaittu!")
    time.sleep(1)
