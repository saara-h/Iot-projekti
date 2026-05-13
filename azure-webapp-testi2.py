import cv2
import time
import json
import requests
from datetime import datetime, timezone
from grove.gpio import GPIO
import RPi.GPIO as RPIO

from FaceReg import cam_face
from FaceReg import Buzzer2


# ======================================================
# AZURE WEB APP - API
# ======================================================
API_URL = "https://iot-projec-m.azurewebsites.net/add"


# ======================================================
# FACE RECOGNITION - ALUSTUS
# ======================================================
[Data_list, Datafile] = cam_face.getData()
face_r = cam_face.initialize_recognizer()


# ======================================================
# LÄHETYS AZURE WEB APPiin (HTTP POST)
# ======================================================
def send_to_web_app(event_data):
    try:
        response = requests.post(
            url=API_URL,
            json=event_data,
            timeout=5
        )

        if response.status_code == 200:
            print("✅ Lähetetty Web Appiin:")
            print(json.dumps(event_data, indent=2))
        else:
            print(
                f"⚠️ Web App vastasi virheellä "
                f"({response.status_code}): {response.text}"
            )

    except requests.exceptions.RequestException as e:
        print("❌ HTTP-yhteysvirhe:", e)


# ======================================================
# MANUAALINEN TILANVAIHTO NÄPPÄIMISTÖLTÄ
# ======================================================
def mode_chage_manual(mode):
    key = cv2.waitKey(1) & 0xFF

    if key == 255 or key == -1:
        return mode
    elif key == ord("q"):
        return "break"
    elif key == ord("c"):
        return "c"
    elif key == ord("r"):
        return "r"
    elif key == ord("b"):
        return "b"

    return mode


# ======================================================
# PÄÄOHJELMA
# ======================================================
def main():
    RPIO.setmode(RPIO.BCM)
    RPIO.setup(5, GPIO.IN)

    mode = "r"        # käytetään buzzer + recognition ‑tilaa
    beeb_gab = 5

    tone_known = [[3000], 0.5]
    tone_unknown = [[800, 400], 0.25]

    while True:

        # ==================================================
        # LIIKETUNNISTUS KÄYNNISTÄÄ SESSION
        # ==================================================
        if RPIO.input(5):
            print("🚨 Motion detected – session started")

            # -------- SESSION DATA --------
            session = {
                "startTime": datetime.now(timezone.utc),
                "facesDetected": False,
                "personRecognized": False,
                "personName": None,
                "bestConfidence": None
            }

            cap = cv2.VideoCapture(0)
            start_time = time.time()
            duration = 20
            beeb_start = time.time()
            played = False

            # ==================================================
            # SESSION AIKAINEN KAMERA
            # ==================================================
            while True:

                if (time.time() - beeb_start) >= beeb_gab:
                    played = False
                    beeb_start = time.time()

                if cap.grab():
                    _, image = cap.retrieve()
                    mode = mode_chage_manual(mode)

                    if mode == "break":
                        break

                    result = cam_face.recognize_buzzer(
                        face_r, image, played
                    )

                    cv2.imshow("Faces Found", image)

                    # -------- TUNNISTUSTULOS --------
                    if result is not None:
                        session["facesDetected"] = True
                        confidence = result["confidence"]

                        # ✅ TUNNETTU
                        if result["recognized"]:
                            if not played:
                                Buzzer2.play_tone(
                                    tone_known[0], tone_known[1]
                                )
                                played = True

                            # valitaan paras (PIENIN) confidence koko session ajalta
                            if (
                                session["bestConfidence"] is None or
                                confidence < session["bestConfidence"]
                            ):
                                session["personRecognized"] = True
                                session["personName"] = result["name"]
                                session["bestConfidence"] = confidence

                            print(
                                f"👤 Tunnistettu: {result['name']} "
                                f"(confidence={confidence:.2f})"
                            )

                        # ❌ TUNTEMATON
                        else:
                            if not played:
                                Buzzer2.play_tone(
                                    tone_unknown[0], tone_unknown[1]
                                )
                                played = True

                            if session["bestConfidence"] is None:
                                session["bestConfidence"] = confidence

                            print(
                                f"❓ Tuntematon henkilö "
                                f"(confidence={confidence:.2f})"
                            )

                # ==================================================
                # SESSION PÄÄTTYMINEN
                # ==================================================
                if time.time() - start_time > duration:
                    print("📴 Kamera sammutetaan – session päättyy")

                    final_event = {
                        "timestamp": session["startTime"].isoformat(),
                        "endTime": datetime.now(timezone.utc).isoformat(),
                        "eventType": "motion_session",
                        "motionDetected": True,
                        "facesDetected": session["facesDetected"],
                        "personRecognized": session["personRecognized"],
                        "personName": session["personName"],
                        "bestConfidence": session["bestConfidence"],
                        "deviceId": "raspberrypi-1"
                    }

                    send_to_web_app(final_event)
                    break

                cv2.waitKey(1)

            cap.release()
            cv2.destroyAllWindows()
            time.sleep(5)

        if mode == "break":
            break

        time.sleep(0.2)

    Datafile.close()


# ======================================================
# KÄYNNISTYS
# ======================================================
if __name__ == "__main__":
    main()
