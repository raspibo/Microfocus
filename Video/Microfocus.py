# USAGE
# python Microfocus.py 
# Detect blurry video, and print a value of blur calculatd by variance of laplacian

# import the necessary packages
from imutils import paths
import numpy as np
import argparse
import cv2
import numpy as np
import matplotlib.pyplot as plt
import serial
import time
import io

scan=0
val=0
last_val=0
last_fm=0.0
scan_list=[]
#Serial takes these two parameters: serial device and baudrate
ser = serial.Serial('/dev/ttyUSB0', 115200)
#ser.write(b'+')
#data = ser.readline()
#print(data)

def variance_of_laplacian(image):
	# compute the Laplacian of the image and then return the focus
	# measure, which is simply the variance of the Laplacian
	return cv2.Laplacian(image, cv2.CV_64F).var()

def hconcat_resize_min(im_list, interpolation=cv2.INTER_CUBIC):
	h_min = min(im.shape[0] for im in im_list)
	im_list_resize = [cv2.resize(im, (int(im.shape[1] * h_min / im.shape[0]), h_min), interpolation=interpolation)
		for im in im_list]
	return cv2.hconcat(im_list_resize)

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dev", required=True,
	help="video device number X es /dev/videoX")
ap.add_argument("-t", "--threshold", type=float, default=100.0,
	help="focus measures that fall below this value will be considered 'blurry'")
ap.add_argument('-b', '--bins', type=int, default=16,
	help='Number of bins per channel (default 16)')
ap.add_argument('-w', '--width', type=int, default=0,
	help='Resize video to specified width in pixels (maintains aspect)')
args = vars(ap.parse_args())

dev=int(args["dev"])
print(dev)
cap = cv2.VideoCapture(dev)
cap.set(3,1024)
cap.set(4,768)
cap.set(5,60)
cap.set(15, 0.1)
bins = args['bins']
resizeWidth = args['width']

# Create a black image
img = np.zeros((720,720,3), np.uint8)

# Draw a blue line with thickness of 5 px
#cv2.line(img,(15,20),(15,20),(255,0,0),5)

#Display the image
#cv2.imshow("img",img)


while(True):
	if scan == 1:
		b_val=str(val)
		ser.write(str.encode(b_val))
		ser.write(b'\r')
		val=val+1
		if val== 190 :
			scan = 0
			print("Scan end")
			print("Best value: {}".format(max(scan_list)))
			print("at value: {}".format(scan_list.index(max(scan_list))))
		time.sleep(.2)
	# load the image, convert it to grayscale, and compute the
	# focus measure of the image using the Variance of Laplacian
	# method
	#image = cv2.imread(imagePath)
	# Capture frame-by-frame
	ret, frame = cap.read()
	#gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# Our operations on the frame come here
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	fm = variance_of_laplacian(gray)
	text = "Not Blurry"

	# if the focus measure is less than the supplied threshold,
	# then the image should be considered "blurry"
	if fm < args["threshold"]:
		text = "Blurry"

	# show the image
	#cv2.putText(image, "{}: {:.2f}".format(text, fm), (10, 30),
	#	cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
	cv2.putText(frame, "{}: {:.2f} - val: {}".format(text, fm, val), (10, 30),
		cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
	#print("{}: {:.2f}".format(text, fm))
	#cv2.imshow("Image", image)
	#cv2.imshow("Frame", frame)

	# Draw a point with val and fm on graph
	if scan == 1:
		scan_list.append(fm)
		cv2.line(img,(last_val*3,int(last_fm)),(val*3,int(fm)),(255,255,255),3)
		last_val=val
		last_fm=fm
		cv2.rectangle(img,(5,5),(250,50),(0,0,0),-15)
		cv2.putText(img, "val: {} {:.2f}".format(val, fm), (10, 30),
			cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)

	#im_h = cv2.hconcat([img, frame])
	im_h = hconcat_resize_min([img, frame])
	cv2.imshow("Frame", im_h)

	key=cv2.waitKey(5) & 0xFF
	if key == ord('+'):
		ser.write(b'+')
		val=val+1
	if key == ord('-'):
		ser.write(b'-')
		val=val-1
	if key == ord('s'):
		val=0
		print("Scan start\r")
		cv2.destroyWindow("img"); 
		cv2.destroyWindow("im_h"); 
		img = np.zeros((720,720,3), np.uint8)
		scan=1
	if key == ord('q'):
		break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
