# adapted from https://projects.raspberrypi.org/en/projects/raspberry-pi-zero-time-lapse-cam/4
import time
from time import sleep

import picamera

WAIT_TIME = 60

with picamera.PiCamera() as camera:
    for filename in camera.capture_continuous(f'images/img{int(time.time())}.jpg'):
        print(f"took a photo at {time.time()}")
        sleep(WAIT_TIME)
