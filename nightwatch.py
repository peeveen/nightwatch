import yaml
import picamera

config_path="./nightwatch.yml"
config = yaml.safe_load(open(config_path))
path = config["path"]
seconds = int(config["seconds"])
byteDiffThreshold = int(config["byteDiffThreshold"])
print(f"Saving files to {path} every {seconds} seconds.")
print(f"Files that do not differ in size from the previous one by {byteDiffThreshold} bytes will be discarded.")
while(True):
    
