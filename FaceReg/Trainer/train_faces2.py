import cv2
import sys
import os
import random

sys.argv=[sys.argv[0], 'Milja']

global directory_path
directory_path = os.path.dirname(os.path.abspath(__file__))
face_dir=directory_path.rpartition("\\")[0]
if face_dir=='':
    face_dir=directory_path.rpartition("/")[0]
cascade = face_dir+"/face_cascade.xml"
face_cascade=cv2.CascadeClassifier(cascade)
dir_path = False


def detect(image_path, name):
    abs_in = os.path.abspath(image_path)
    image = cv2.imread(abs_in)
    if image is None:
        print("Could not read image:", abs_in)
        return

    cv2.imshow("Faces Found", image)
    cv2.waitKey(1)

    image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        image_grey,
        scaleFactor=1.16,
        minNeighbors=5,
        minSize=(25, 25),
        flags=0
    )

    for x, y, w, h in faces:
        sub_img = image[y:y+h, x:x+w]

        dataset_dir = face_dir+"/Dataset"
        os.makedirs(dataset_dir, exist_ok=True)

        out_name = f"{name}{random.randint(0, 100000000)}.jpg"
        out_path = os.path.join(dataset_dir, out_name)

        ok = cv2.imwrite(out_path, sub_img)
        if not ok:
            print("Failed to write:", out_path)



def main():
    if len(sys.argv) != 2:
        print("Usage: python train_faces.py <Name of person>")
        sys.exit()

    name = sys.argv[1]

    folder_path = directory_path+"/"+sys.argv[1]+"/"

    if not os.path.exists(folder_path):
        print("No images exist for the given person")
        sys.exit()

    os.chdir(folder_path)
    
    print("Creating Proper Dataset.......")
    images_exist = False
    for img in os.listdir("."):
        if img.lower().endswith('.jpg') or img.lower().endswith('.png') or img.lower().endswith('.jpeg'):
            detect(img, name)
            images_exist = True
    print("Done")
    if not images_exist:
        print("No images found to create a dataset")

if __name__ == "__main__":
    main()

