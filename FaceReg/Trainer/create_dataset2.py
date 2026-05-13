import cv2
import random
import os
import sys

#Kovakoodattu nimen määritys
#sys.argv=[sys.argv[0], "Milja"]

cap = cv2.VideoCapture(0)


def start(directory_name):
	count=0
	speed=10
	#while True:
	while count <= 500:
		if cap.grab():
			RET, IMAGE = cap.retrieve()
			if not RET:
				continue
			count+=1
			cv2.putText(IMAGE, f"Frames: {count} | Saved: {count//speed}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
			if count%speed == 0:
				cv2.imwrite(str(random.uniform(0, 100000)) + ".jpg", IMAGE)
			cv2.imshow("Video", IMAGE)
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
	cap.release()
	cv2.destroyAllWindows()


def main():
	os.chdir(os.path.dirname(os.path.abspath(__file__)))
	if len(sys.argv) != 2:
		print("Usage: python create_dataset.py <Name of the person>")
		sys.exit()

	name = sys.argv[1]
	name = "./"+name

	if os.path.exists(name):
		print("name already exists")
		name = name+str(random.randint(0, 10000))
		print("So, the dataset has been saved as" + name)
    
	os.makedirs(name)
	os.chdir(name)

	start(name)


if __name__ == "__main__":
	main()
