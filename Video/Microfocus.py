#!/usr/bin/python3
# USAGE
# python3 Microfocus.py 
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
#ser = serial.Serial('/dev/ttyUSB0', 115200)
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
ap = argparse.ArgumentParser(description='A simple and low cost kit for microscope focus. Thi is a opencv/python utility. You can use some keys inside app: +, -, s, q.')

ap.add_argument("-c", "--cap", type=int, default=0,
        help="Set to 1 to print a property in the VideoCapture (opencv https://docs.opencv.org/2.4/modules/highgui/doc/reading_and_writing_images_and_video.html)")
ap.add_argument("-d", "--dev", default=0,
        help="video device number X es /dev/videoX default 0")
ap.add_argument("-p", "--port", default='ttyUSB0',
        help="serial device es /dev/XXXXXX where XXXXXX es ttyUSB0 (default)")
ap.add_argument("-t", "--threshold", type=float, default=100.0,
        help="focus measures that fall below this value will be considered 'blurry'")
ap.add_argument('-b', '--bins', type=int, default=16,
        help='Number of bins per channel (default 16)')
ap.add_argument('-g', '--geom',type=str,default='1280x720',
        help='Resize video to specified width in pixels (maintains aspect)')
ap.add_argument('-s', '--scan', type=int, default=0,
        help='set to 1 to start with focus scan. Check for a max extension of slider!')
args = vars(ap.parse_args())

#Serial takes these two parameters: serial device and baudrate
ser = serial.Serial('/dev/' + args['port'] , 115200)

dev=int(args["dev"])
print("Video device {}".format(dev))
print("Serial device {}".format(ser))

cap = cv2.VideoCapture(dev)
captureproprities=["CV_CAP_PROP_POS_MSEC", "CV_CAP_PROP_POS_FRAMES", "CV_CAP_PROP_POS_AVI_RATIO", "CV_CAP_PROP_FRAME_WIDTH", "CV_CAP_PROP_FRAME_HEIGHT", "CV_CAP_PROP_FPS", "CV_CAP_PROP_FOURCC", "CV_CAP_PROP_FRAME_COUNT", "CV_CAP_PROP_FORMAT", "CV_CAP_PROP_MODE", "CV_CAP_PROP_BRIGHTNESS", "CV_CAP_PROP_CONTRAST", "CV_CAP_PROP_SATURATION", "CV_CAP_PROP_HUE", "CV_CAP_PROP_GAIN", "CV_CAP_PROP_EXPOSURE", "CV_CAP_PROP_CONVERT_RGB", "CV_CAP_PROP_WHITE_BALANCE_U", "CV_CAP_PROP_WHITE_BALANCE_V", "CV_CAP_PROP_RECTIFICATION", "CV_CAP_PROP_ISO_SPEED", "CV_CAP_PROP_BUFFERSIZE"]

if args['cap'] == 1 :
	print("Default cap property of camera:")
	for x in range(22):
		print(str(x) + ") " + captureproprities[x] + ": \t " + str(cap.get(x)))

#params from https://docs.opencv.org/2.4/modules/highgui/doc/reading_and_writing_images_and_video.html
#CV_CAP_PROP_FRAME_WIDTH
width=int(args["geom"].split('x',1)[0])
cap.set(3,width)	
#CV_CAP_PROP_FRAME_HEIGHT
height=int(args["geom"].split('x',1)[1])
cap.set(4,height)
#CV_CAP_PROP_FPS
cap.set(5,30)
#CAP_PROP_EXPOSURE 
cap.set(15, 0.75)
#CV_CAP_PROP_ISO_SPEED
cap.set(20, 1.0)
bins = args['bins']


if args['cap'] == 1 :
	print("Current cap property of camera:")
	for x in range(22):
		print(str(x) + ") " + captureproprities[x] + ": \t " + str(cap.get(x)))

# Create a black image
img = np.zeros((width,width,3), np.uint8)

# Draw a blue line with thickness of 5 px
#cv2.line(img,(15,20),(15,20),(255,0,0),5)

#Display the image
#cv2.imshow("img",img)

graph = cv2.CreateImage((800,600), 1, 1)

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
	if key == ord('s') or args['scan'] == 1 :
		args['scan']=0
		val=0
		print("Scan start\r")
		cv2.destroyWindow("img"); 
		cv2.destroyWindow("im_h"); 
		img = np.zeros((width,width,3), np.uint8)
		scan=1
	if key == ord('q'):
		break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
