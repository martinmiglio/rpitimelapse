# adapted from https://projects.raspberrypi.org/en/projects/raspberry-pi-zero-time-lapse-cam/4
import time
from time import sleep

import picamera

WAIT_TIME = 60

with picamera.PiCamera() as camera:
    camera.resolution = (1024, 768)
    for filename in camera.capture_continuous(f'images/img{time.time()}.jpg'):
        sleep(WAIT_TIME)
