
import cv2
import time
from grove.gpio import GPIO
import cam_face


'''global SCRIPT_DIR, FONT, FACE_CASCADE, Data_list, Datafile
[SCRIPT_DIR, FONT,FACE_CASCADE, Data_list, Datafile]=cam_face.constants()'''
#global Data_list, Datafile
[Data_list,Datafile]=cam_face.getData()


#global face_r
face_r=cam_face.initialize_recognizer()

BUZZER_PIN = PWM
#global buzzer
buzzer = GPIO(PWM, GPIO.OUT)

pir = GPIO(14, GPIO.IN) # this too

#global cap
cap = cv2.VideoCapture(0)



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
    mode='c'
    played=False

    beeb_gab=15
    tone_known=(1000,2)
    tone_unknown=(4000,4)
    while True:
        if pir.read():
            print("Motion detected!")
            
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
                        cam_face.recognize_buzzer(face_r,image,tone_known,tone_unknown,played,buzzer)
            cap.release()
            cv2.destroyAllWindows()
            
            time.sleep(5)
        if mode=='break':
            break
        time.sleep(0.2)
    Datafile.close()


if __name__=='__main__':
    main()
