import datetime
import io
import os
import time

from libcamera import Transform
from picamera2 import Picamera2


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

path="/images"
seconds = int(os.environ.get("FREQUENCY_SECONDS"))
resolution_x = int(os.environ.get("RESOLUTION_X"))
resolution_y = int(os.environ.get("RESOLUTION_Y"))
flip_x = int(os.environ.get("FLIP_X"))
flip_y = int(os.environ.get("FLIP_Y"))
imageLifespanDays = int(os.environ.get("IMAGE_LIFESPAN_DAYS"))
byteDiffThreshold = int(os.environ.get("BYTE_DIFFERENCE_THRESHOLD"))

print(f"Saving images of {resolution_x}x{resolution_y} resolution to {path} every {seconds} seconds.")
print(f"Files that do not differ in size from the previous one by at least {byteDiffThreshold} bytes will be discarded.")
print(f"Images will be kept for {imageLifespanDays} days")
camera = Picamera2()
camera_config = camera.create_still_configuration(main={"size": (resolution_x,resolution_y)}, transform=Transform(hflip=flip_x, vflip=flip_y), display="main")
camera.configure(camera_config)
camera.start()
previousImageSize = 0
while(True):
	with io.BytesIO() as stream:
		now = datetime.datetime.now()
		cleanup(now, path, imageLifespanDays)
		folder = f"{now.year}{str(now.month).zfill(2)}{str(now.day).zfill(2)}"
		folderPath=os.path.join(path,folder)
		if(not os.path.exists(folderPath)):
			os.mkdir(folderPath)
		camera.capture(stream, format="jpeg")
		stream.seek(0)
		currentImageSize = stream.getbuffer().nbytes
		if(abs(previousImageSize-currentImageSize)< byteDiffThreshold):
			print("Current image not sufficiently different; discarding.")
		else:
			filename = f"{str(now.hour).zfill(2)}{str(now.minute).zfill(2)}{str(now.second).zfill(2)}.jpg" 
			imagePath = os.path.join(folderPath, filename)
			print(f"Writing to {imagePath} ...")
			with open(imagePath, "wb") as f:
				f.write(stream.getbuffer())
			previousImageSize = currentImageSize
	print("Waiting ...")
	time.sleep(seconds)
camera.stop()
