# adapted from https://projects.raspberrypi.org/en/projects/raspberry-pi-zero-time-lapse-cam/4
import time
from time import sleep

import picamera

WAIT_TIME = 60

with picamera.PiCamera() as camera:
    camera.resolution = (852, 480)
    while True:
        camera.capture(f'images/img{int(time.time())}.jpg')
        print(f"took a photo at {int(time.time())}")
        sleep(WAIT_TIME)
