from grove.gpio import GPIO
import time
import cv2

pir = GPIO(5, GPIO.IN)  # D5-portti

while True:
    if pir.read():
        print("Liikettä havaittu!")

        # Käynnistä kamera vasta tässä
        cap = cv2.VideoCapture(0)

        start_time = time.time()
        capture_duration = 5   # sekuntia

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            cv2.imshow("Webcam", frame)
            
            

            # Sammuta kamera kun aika täyttyy
            if time.time() - start_time > capture_duration:
                print("Kamera sammutetaan...")
                break
            cv2.waitKey(1)
        # Vapauta kamera ja sulje ikkuna
        cap.release()
        cv2.destroyAllWindows()

        # Pieni tauko, ettei kamera käynnisty heti uudelleen
        time.sleep(5)

    time.sleep(0.2)
