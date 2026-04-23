import cv2
import sys
import os
import re
import numpy as np
import shelve,random
import glob
#sys.argv = [sys.argv[0],'Facefold']

FONT = cv2.FONT_HERSHEY_SIMPLEX
script_dir = os.path.dirname(os.path.abspath(__file__))
CASCADE = os.path.join(script_dir, "face_cascade.xml")
FACE_CASCADE = cv2.CascadeClassifier(CASCADE)

print("Cascade loaded:", not FACE_CASCADE.empty())

script_dir = os.path.dirname(os.path.abspath(__file__))
Datafile = shelve.open(os.path.join(script_dir, "Data.db"))
print(Datafile)
if 'Data' not in Datafile.keys():
    Datafile['Data']=list()
    Data_list = list()
else:
    Data_list = Datafile["Data"]


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


#def add_to_dataset(image):
def initialize_recognizer():
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    print("Training..........")
    Dataset = get_images(script_dir+"/Dataset")
    print("Recognizer trained using Dataset: "+str(Dataset[2])+" Images used")
    face_recognizer.train(Dataset[0],np.array(Dataset[1]))
    return face_recognizer


def resize_to_screen(img, max_height=1200):
    h, w = img.shape[:2]
    if h > max_height:
        scale = max_height / h
        new_w, new_h = int(w * scale), int(h * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return img


def save_wrong_faces(num_wrong: list, temp_set: list, correct_name: list):
    os.makedirs("./Dataset", exist_ok=True)
    
    # Wrong predictions
    for i in range (len(num_wrong)):
        if num_wrong[i]=='y':
                name=correct_name[i]
                if name != "nil":
                    cv2.imwrite(f"./Dataset/{name}{random.uniform(0,100000):.0f}.jpg", temp_set[i])


def process_single_image(image_paths: list, face_recognizer):
    images = []
    for path in image_paths:
        image = cv2.imread(path)
        if image is None: continue
        image = resize_to_screen(image)
        images.append(image)
    
    if not images: return
    
    all_temp_set, all_face_list = [], []
    wrong_list, correct_name=[], []

    for i, image in enumerate(images):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = FACE_CASCADE.detectMultiScale(gray, 1.1, 3, minSize=(10,10))
        
        for x,y,w,h in faces:
            sub_img = gray[y:y+h,x:x+w]
            img_crop = image[y:y+h,x:x+w]
            all_temp_set.append(img_crop)
            
            nbr, conf = face_recognizer.predict(sub_img)
            all_face_list.append([nbr, conf])
            
            cv2.rectangle(image,(x-5,y-5),(x+w+5,y+h+5),(255,255,0),2)
            cv2.putText(image,Data_list[nbr],(x,y-10),FONT,0.5,(255,255,0),1)
        
        cv2.imwrite(f"Detected_{i+1}.jpg", image)
        cv2.imshow(f'Img {i+1}', image)
        cv2.waitKey(0); cv2.destroyAllWindows()
        
        wrong=input("Wrong face? (y): ")
        name='zero'
        if wrong.lower()=='y':
            name=input("Correct name: ")
        correct_name.append(name)
        wrong_list.append(wrong)

    save_wrong_faces(wrong_list, all_temp_set, correct_name)


def recognize_from_folder(folder_path, face_recognizer):
    image_paths = []
    for ext in ['*.jpg','*.jpeg','*.png','*.bmp','*.tiff']:
        image_paths.extend(glob.glob(os.path.join(folder_path, '**', ext), recursive=True))
    
    process_single_image(image_paths, face_recognizer)

    

def recognize_video(face_recognizer):
    FONT = cv2.FONT_HERSHEY_SIMPLEX
    script_dir = os.path.dirname(os.path.abspath(__file__))
    CASCADE = os.path.join(script_dir, "face_cascade.xml")
    FACE_CASCADE = cv2.CascadeClassifier(CASCADE)
    
    print("Cascade loaded:", not FACE_CASCADE.empty())
    cap = cv2.VideoCapture(0)
    while True:
        if cap.grab():
            ref,image = cap.retrieve()
            image_grey=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
            faces = FACE_CASCADE.detectMultiScale(image_grey,scaleFactor=1.16,minNeighbors=5,minSize=(40,40),flags=0)
        for x,y,w,h in faces: #Koko^^^^^^ def MinNeig.=5, MinSize=40,40, Flags=0
            sub_img=image_grey[y:y+h,x:x+w]
            img=image[y:y+h,x:x+w]
            nbr,conf = face_recognizer.predict(sub_img)
            cv2.rectangle(image,(x-5,y-5),(x+w+5,y+h+5),(255, 255,0),2)
            if conf<60: #Herkkyyden säätö def=80 app.=75-100
                cv2.putText(image,Data_list[nbr],(x,y-10), FONT, 0.5,(255,255,0),1)
            else:
                cv2.putText(image,'Unknown',(x,y-10), FONT, 0.5,(255,0,0),1)
        cv2.imshow("Faces Found",image)
        if (cv2.waitKey(1) & 0xFF == ord('q')) or (cv2.waitKey(1) & 0xFF == ord('Q')):
            break
    Datafile["Data"]=Data_list
    Datafile.close()
    cap.release()
    cv2.destroyAllWindows()


def start(face_r):
    if len(sys.argv) not in [1, 2]:
        print("Usage: python face_recog.py [<complete image_path>]")
        sys.exit()

    #face_r = initialize_recognizer()

    if len(sys.argv)==1:
        recognize_video(face_r)
    else:
        path = sys.argv[1]
        if os.path.isfile(path):
            process_single_image(path, face_r, 1)
        elif os.path.isdir(path):
            recognize_from_folder(path, face_r)
        else:
            print("Not a file or folder")


if __name__ == "__main__":
    main()
