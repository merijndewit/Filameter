from picamera import PiCamera
from PIL import Image
import time
import os

from io import BytesIO
from time import sleep

import PerformanceTimer as pt

camera = PiCamera()
camera.resolution = (2000, 500)
camera.framerate = 24

def CaptureImage(save=False):
    pt.StartTimer()
    stream = BytesIO()

    #camera.start_preview()
    #sleep(0.1)
    camera.capture(stream, format='png')
    #camera.stop_preview()

    stream.seek(0)
    image = Image.open(stream)

    if save:
        image.save(os.path.dirname(os.path.realpath(__file__)) + "/CapturedImages/capture.png")

    pt.StopTimer("capturing image")
    return image

def Preview():
    camera.start_preview()
    time.sleep(20)
    camera.stop_preview()
