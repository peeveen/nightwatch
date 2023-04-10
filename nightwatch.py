import yaml
from picamera import PiCamera
import time
import datetime
import os

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

config_path="./nightwatch.yml"
config = yaml.safe_load(open(config_path))
path = config["path"]
seconds = int(config["seconds"])
resolution = config["resolution"]
imageLifespanDays = int(config["imageLifespanDays"])
byteDiffThreshold = int(config["byteDiffThreshold"])
print(f"Saving images of {resolution} resolution to {path} every {seconds} seconds.")
print(f"Files that do not differ in size from the previous one by at least {byteDiffThreshold} bytes will be discarded.")
print(f"Images will be kept for {imageLifespanDays} days")
camera = PiCamera()
camera.rotation=180
camera.resolution=resolution
previousImageSize = 0
while(True):
	now = datetime.datetime.now()
	cleanup(now, path, imageLifespanDays)
	folder = f"{now.year}{str(now.month).zfill(2)}{str(now.day).zfill(2)}"
	filename = f"{str(now.hour).zfill(2)}{str(now.minute).zfill(2)}{str(now.second).zfill(2)}.jpg" 
	folderPath=os.path.join(path,folder)
	if(not os.path.exists(folderPath)):
		os.mkdir(folderPath)
	imagePath = os.path.join(folderPath, filename)
	print(f"Writing to {imagePath} ...")
	camera.capture(imagePath)
	currentImageSize = os.path.getsize(imagePath)
	if(abs(previousImageSize-currentImageSize)< byteDiffThreshold):
		print("Current image not sufficiently different; discarding.")
		os.remove(imagePath)
	else:
		previousImageSize = currentImageSize
	print("Waiting ...")
	time.sleep(seconds)
