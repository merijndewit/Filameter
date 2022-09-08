from picamera import PiCamera
import time
import os
camera = PiCamera()

def CaptureImage():
    camera.start_preview()
    time.sleep(2)
    camera.capture(os.path.dirname(os.path.realpath(__file__)) + "/CapturedImages/capture.png")
    camera.stop_preview()

def Preview():
    camera.start_preview()
    time.sleep(20)
    camera.stop_preview()
