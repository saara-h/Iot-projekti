
import cv2
import sys, os
import time
import shelve, re
import numpy as np
from FaceReg import Buzzer

FONT = cv2.FONT_HERSHEY_SIMPLEX
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CASCADE = os.path.join(SCRIPT_DIR, "face_cascade.xml")
FACE_CASCADE = cv2.CascadeClassifier(CASCADE)


def getData():
    Datafile = shelve.open(os.path.join(SCRIPT_DIR, "Data.db"))

    if 'Data' not in Datafile.keys():
        Datafile['Data']=list()
        Data_list = list()
    else:
        Data_list = Datafile["Data"]
    return (Data_list,Datafile)

[Data_list,Datafile]=getData()

'''
def constants():
    FONT = cv2.FONT_HERSHEY_SIMPLEX
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    CASCADE = os.path.join(SCRIPT_DIR, "face_cascade.xml")
    FACE_CASCADE = cv2.CascadeClassifier(CASCADE)

    Datafile = shelve.open(os.path.join(SCRIPT_DIR, "Data.db"))

    if 'Data' not in Datafile.keys():
        Datafile['Data']=list()
        Data_list = list()
    else:
        Data_list = Datafile["Data"]
        return (SCRIPT_DIR,FONT,FACE_CASCADE,Data_list,Datafile)
'''

def Make_Changes(label):
    if label not in Data_list:
        Data_list.append(label)
    print(Data_list)


def get_images(path):
    images = list()
    labels = list()
    count=0
    if len(os.listdir(path)) == 0:
        print ("Empty Dataset.......aborting Training")
        exit()
    for img in os.listdir(path):
        regex = re.compile(r'(\d+|\s+)')
        labl = regex.split(img)
        labl = labl[0]
        count=count+1
        Make_Changes(labl)
        image_path =os.path.join(path,img)
        image=cv2.imread(image_path)
        image_grey=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        images.append(image_grey)
        labels.append(Data_list.index(labl))
    return images,labels,count


def initialize_recognizer():
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    print("Training..........")
    Dataset = get_images(os.path.join(SCRIPT_DIR, "Dataset"))
    print("Recognizer trained using Dataset: "+str(Dataset[2])+" Images used")
    face_recognizer.train(Dataset[0],np.array(Dataset[1]))
    return face_recognizer


###########################


def recognize(face_recognizer,image):

    image_grey=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    faces = FACE_CASCADE.detectMultiScale(image_grey,scaleFactor=1.16,minNeighbors=5,minSize=(25,25),flags=0)

    for x,y,w,h in faces:
        sub_img=image_grey[y:y+h,x:x+w]
        img=image[y:y+h,x:x+w]
        nbr,conf = face_recognizer.predict(sub_img)
        cv2.rectangle(image,(x-5,y-5),(x+w+5,y+h+5),(255, 255,0),2)

        if conf<60:
            cv2.putText(image,Data_list[nbr],(x,y-10), FONT, 0.5,(255,255,0),1)
        else:
            cv2.putText(image,'Unknown',(x,y-10), FONT, 0.5,(255,255,0),1)



def recognize_buzzer(face_recognizer,image,played):

    image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = FACE_CASCADE.detectMultiScale(
        image_grey,
        scaleFactor=1.16,
        minNeighbors=5,
        minSize=(25, 25),
        flags=0
    )

    # Ei kasvoja
    if len(faces) == 0:
        return None

    for x, y, w, h in faces:
        sub_img = image_grey[y:y+h, x:x+w]

        label_id, confidence = face_recognizer.predict(sub_img)

        cv2.rectangle(
            image,
            (x-5, y-5),
            (x+w+5, y+h+5),
            (255, 255, 0),
            2
        )

        THRESHOLD = 60  # sama logiikka kuin aiemmin

        # ✅ TUNNETTU
        if confidence < THRESHOLD:
            name = Data_list[label_id]
            cv2.putText(
                image,
                name,
                (x, y-10),
                FONT,
                0.5,
                (255, 255, 0),
                1
            )

            return {
                "recognized": True,
                "name": name,
                "confidence": float(confidence)
            }

        # ❌ TUNTEMATON
        else:
            cv2.putText(
                image,
                "Unknown",
                (x, y-10),
                FONT,
                0.5,
                (255, 255, 0),
                1
            )

            return {
                "recognized": False,
                "name": None,
                "confidence": float(confidence)
            }
    
#    image_grey=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
#    faces = FACE_CASCADE.detectMultiScale(image_grey,scaleFactor=1.16,minNeighbors=5,minSize=(25,25),flags=0)
#
#    for x,y,w,h in faces:
#        sub_img=image_grey[y:y+h,x:x+w]
#        img=image[y:y+h,x:x+w]
#        nbr,conf = face_recognizer.predict(sub_img)
#        cv2.rectangle(image,(x-5,y-5),(x+w+5,y+h+5),(255, 255,0),2)
#
#        if conf<60:
#            cv2.putText(image,Data_list[nbr],(x,y-10), FONT, 0.5,(255,255,0),1)
#            if not played:
#                #Buzzer.play_tone(tone_known[0],tone_known[1],buzzer)
#                #played = True
#                return True
#        else:
#            cv2.putText(image,'Unknown',(x,y-10), FONT, 0.5,(255,255,0),1)
#            if not played:
#                    #Buzzer.play_tone(tone_unknown[0],tone_unknown[1],buzzer)
#                    #played = True
#                    return False           


