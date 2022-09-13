from picamera import PiCamera
import time
import os

import PerformanceTimer as pt

camera = PiCamera()
camera.resolution = (2000, 500)

def CaptureImage():
    pt.StartTimer()
    camera.start_preview()
    time.sleep(0.1)
    camera.capture(os.path.dirname(os.path.realpath(__file__)) + "/CapturedImages/capture.png")
    camera.stop_preview()
    pt.StopTimer("capturing image")

def Preview():
    camera.start_preview()
    time.sleep(20)
    camera.stop_preview()
