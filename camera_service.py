
from sys import exit
from time import sleep, time

try:
    import picamera
except ModuleNotFoundError:
    print("not running on raspberry pi!")
    exit()
else:
    WAIT_TIME = 60

    with picamera.PiCamera() as camera:
        camera.resolution = (1280, 720)
        while True:
            camera.capture(f'images/img{int(time())}.jpg')
            print(f"took a photo at {int(time())}")
            sleep(WAIT_TIME)
