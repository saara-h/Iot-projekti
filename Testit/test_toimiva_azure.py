import cv2
import time
import json
from datetime import datetime
from grove.gpio import GPIO
import RPi.GPIO as RPIO
from FaceReg import cam_face
from FaceReg import Buzzer2

from azure.iot.device import IoTHubDeviceClient, Message


# ======================================================
# IOT HUB - YHTEYS
# ======================================================
CONNECTION_STRING = "HostName=RaspiHub1.azure-devices.net;DeviceId=raspi1;SharedAccessKey=ho2OxkTKrc0tV+ttpd+0omN7tI29OCAnKvjZ+OaOv9k="

client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
client.connect()


# ======================================================
# FACE RECOGNITION - ALUSTUS
# ======================================================
[Data_list, Datafile] = cam_face.getData()
face_r = cam_face.initialize_recognizer()


# ======================================================
# TAPAHTUMIEN LUONTI
# ======================================================
def create_event(event_type, person_recognized=None, person_name=None):
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "eventType": event_type,
        "motionDetected": event_type in ["motion", "recognition"],
        "personRecognized": person_recognized,
        "personName": person_name,
        "deviceId": "raspberrypi-1"
    }
    return event


# ======================================================
# LÄHETYS IOT HUBIIN
# ======================================================
def send_to_iot_hub(event_data):
    message_json = json.dumps(event_data)
    message = Message(message_json)
    message.content_type = "application/json"
    message.content_encoding = "utf-8"

    client.send_message(message)
    print("✅ Lähetetty IoT Hubiin:", message_json)


# ======================================================
# MANUAALINEN TILANVAIHTO
# ======================================================
def mode_chage_manual(mode):
    key = cv2.waitKey(1) & 0xFF
    if key == 255 or key == -1:
        return mode
    elif key == ord('q'):
        return 'break'
    elif key == ord('c'):
        return 'c'
    elif key == ord('r'):
        return 'r'
    elif key == ord('b'):
        return 'b'
    return mode


# ======================================================
# PÄÄOHJELMA
# ======================================================
def main():
    RPIO.setmode(RPIO.BCM)
    RPIO.setup(5, GPIO.IN)

    mode = 'r'
    played = False

    beeb_gab = 5
    tone_known = [[3000], 0.5]
    tone_unknown = [[800, 400], 0.25]

    while True:

        # ==================================================
        # LIIKETUNNISTUS
        # ==================================================
        if RPIO.input(5):
            print("🚨 Motion detected!")

            # Lähetä liiketapahtuma AZUREEN
            motion_event = create_event(event_type="motion")
            send_to_iot_hub(motion_event)

            cap = cv2.VideoCapture(0)
            start_time = time.time()
            duration = 20
            beeb_start = time.time()

            while True:

                if (time.time() - beeb_start) >= beeb_gab:
                    played = False
                    beeb_start = time.time()

                if cap.grab():
                    _, image = cap.retrieve()
                    mode = mode_chage_manual(mode)

                    if mode == 'break':
                        break

                    elif mode == 'c':
                        cv2.imshow("Faces Found", image)

                    elif mode == 'r':
                        cam_face.recognize(face_r, image)
                        cv2.imshow("Faces Found", image)

                    elif mode == 'b':
                        event = None  # ✅ KORJAUS: aina alustetaan

                        tunnistettu = cam_face.recognize_buzzer(
                            face_r, image, played
                        )
                        cv2.imshow("Faces Found", image)

                        # ======== TUNNETTU ========
                        if tunnistettu is True:
                            Buzzer2.play_tone(tone_known[0], tone_known[1])
                            played = True
                            print("👤 Tunnistettu")

                            event = create_event(
                                event_type="recognition",
                                person_recognized=True,
                                person_name="KNOWN_PERSON"
                            )

                        # ======== TUNTEMATON ========
                        elif tunnistettu is False:
                            Buzzer2.play_tone(tone_unknown[0], tone_unknown[1])
                            played = True
                            print("❓ Ei tunnistettu")

                            event = create_event(
                                event_type="recognition",
                                person_recognized=False,
                                person_name=None
                            )

                        # ✅ LÄHETÄ VAIN JOS EVENT ON OLEMASSA
                        if event is not None:
                            send_to_iot_hub(event)

                if time.time() - start_time > duration:
                    print("📴 Kamera sammutetaan")
                    break

                cv2.waitKey(1)

            cap.release()
            cv2.destroyAllWindows()
            time.sleep(5)

        if mode == 'break':
            break

        time.sleep(0.2)

    Datafile.close()
    client.disconnect()


# ======================================================
# KÄYNNISTYS
# ======================================================
if __name__ == "__main__":
    main()
