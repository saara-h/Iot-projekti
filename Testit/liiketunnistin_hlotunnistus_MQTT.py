
import cv2
import time
from grove.gpio import GPIO
import RPi.GPIO as RPIO
from FaceReg import cam_face
from FaceReg import Buzzer2
import MQTT

'''global SCRIPT_DIR, FONT, FACE_CASCADE, Data_list, Datafile
[SCRIPT_DIR, FONT,FACE_CASCADE, Data_list, Datafile]=cam_face.constants()'''
#global Data_list, Datafile
[Data_list,Datafile]=cam_face.getData()


#global face_r
face_r=cam_face.initialize_recognizer()


def mode_chage_manual(mode):
    key=cv2.waitKey(1) & 0xFF
    if key==255 or key==-1:
        pass
    elif key==ord('q'):
        mode='break'
    elif key==ord('c'):
        mode='c'
    elif key==ord('r'):
        mode='r'
    elif key==ord('b'):
        mode='b'
    return mode


def main():
    RPIO.setmode(RPIO.BCM)
    RPIO.setup(5, GPIO.IN) # this too
    mode='c'
    played=False

    beeb_gab=5
    tone_known=[[3000],0.5]
    tone_unknown=[[800,400],0.25]

    while True:

        if RPIO.input(5):
            cap = cv2.VideoCapture(0)
            print("Motion detected!")
            motion_time = time.time()
            
            # MQTT-yhteys (yksi per motion-event)
            
            start_time = time.time()
            duration = 20 #sekuntia
            sent = False
            
            beeb_start=time.time()
            while True:
                if (time.time()-beeb_start)>=beeb_gab:
                    played=False
                    beeb_start=time.time()

                if cap.grab():
                    ref,image = cap.retrieve()

                    mode=mode_chage_manual(mode)
                    
                    if mode=='break':
                        break
                    elif mode=='c':
                        cv2.imshow("Faces Found",image)
                    elif mode=='r':
                        cam_face.recognize(face_r,image)
                    elif mode=='b':
                        tunnistettu = cam_face.recognize_buzzer(face_r,image,played)
                        if tunnistettu == True:
                            Buzzer2.play_tone(tone_known[0],tone_known[1])
                            played = True
                            print("tunnistettu")
                            if not sent:
                                MQdata=True
                                sent = True
                            #mode = 'c'
                        elif tunnistettu == False:
                            Buzzer2.play_tone(tone_unknown[0],tone_unknown[1])
                            played = True
                            print("ei tunnistettu")
                            if not sent:
                                MQdata=False
                                sent = True

                # Sammuta kamera kun aika täyttyy
                if time.time() - start_time > duration:
                    print("Kamera sammutetaan...")
                    break
                cv2.waitKey(1)
            
            cap.release()
            cv2.destroyAllWindows()

            ts_client = MQTT.connect()
            if MQdata or MQdata==False:
                MQTT.publish_event(ts_client, known=MQdata, motion_time=motion_time)
            else:
                MQTT.publish_noresult(ts_client, motion_time=motion_time)
            ts_client.disconnect()
            time.sleep(5)
            
        if mode=='break':
            break
        time.sleep(0.2)
        
    Datafile.close()


if __name__=='__main__':
    main()
