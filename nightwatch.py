import datetime
import io
import os
import signal
import time

from libcamera import Transform
from picamera2 import Picamera2
from PIL import Image


def cleanup(now, path,imageLifespanDays):
	for (root,dirs,files) in os.walk(path, topdown=False):
		for dir in dirs:
			fullPath=os.path.join(root,dir)
			if(len(os.listdir(fullPath))==0):
				os.rmdir(fullPath)
		for file in files:
			fullPath=os.path.join(root,file)
			timeCreated=os.path.getctime(fullPath)
			difference = now-datetime.datetime.fromtimestamp(timeCreated)
			if(difference.days>imageLifespanDays):
				os.remove(fullPath)

path=os.environ.get("ROOT_SAVE_PATH")
seconds = int(os.environ.get("FREQUENCY_SECONDS"))
resolution_x = int(os.environ.get("RESOLUTION_X"))
resolution_y = int(os.environ.get("RESOLUTION_Y"))
flip_x = int(os.environ.get("FLIP_X"))
flip_y = int(os.environ.get("FLIP_Y"))
imageLifespanDays = int(os.environ.get("IMAGE_LIFESPAN_DAYS"))
byteDiffThreshold = int(os.environ.get("BYTE_DIFFERENCE_THRESHOLD"))

stop=False
def stopApp():
	stop = True

signal.signal(signal.SIGINT, stopApp)
signal.signal(signal.SIGTERM, stopApp)

print(f"Saving images of {resolution_x}x{resolution_y} resolution to {path} every {seconds} seconds.")
print(f"Files that do not differ in size from the previous one by at least {byteDiffThreshold} bytes will be discarded.")
print(f"Images will be kept for {imageLifespanDays} days")
camera = Picamera2()
camera_config = camera.create_still_configuration(main={"size": (resolution_x,resolution_y)}, transform=Transform(hflip=flip_x, vflip=flip_y), display="main")
camera.configure(camera_config)
camera.start()
previousImageSize = 0
while(not stop):
	now = datetime.datetime.now()
	cleanup(now, path, imageLifespanDays)
	folder = f"{now.year}{str(now.month).zfill(2)}{str(now.day).zfill(2)}"
	folderPath=os.path.join(path,folder)
	if(not os.path.exists(folderPath)):
		os.mkdir(folderPath)
	imageBytes=io.BytesIO()
	image:Image = camera.capture_file(imageBytes,"main","jpeg")
	buffer=imageBytes.getbuffer()
	currentImageSize = buffer.nbytes
	if(abs(previousImageSize-currentImageSize)< byteDiffThreshold):
		print("Current image not sufficiently different; discarding.")
	else:
		filename = f"{str(now.hour).zfill(2)}{str(now.minute).zfill(2)}{str(now.second).zfill(2)}.jpg" 
		imagePath = os.path.join(folderPath, filename)
		print(f"Writing image buffer to {imagePath} ...")
		with open(imagePath, "wb") as f:
			f.write(buffer)
		previousImageSize = currentImageSize
	print("Waiting ...")
	time.sleep(seconds)
camera.stop()
