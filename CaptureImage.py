from picamera import PiCamera
from PIL import Image
import time
import os

from io import BytesIO
from time import sleep

import PerformanceTimer as pt

camera = PiCamera()

camera.framerate = 24

def CaptureImage(captureWidth, captureHeight, save=False):
    pt.StartTimer()
    stream = BytesIO()
    camera.resolution = (captureWidth, captureHeight)


    #camera.capture(stream, format='png')
    camera.capture_sequence([stream])
    stream.truncate()
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
