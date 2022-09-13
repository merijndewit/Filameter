from ast import arguments
from tkinter import *

import CaptureImage as captureImage
import ImageProcessing as imageProcessing
import ImageManager as imageManager
import PerformanceTimer as pt
import threading

root = Tk()

#capture = imageManager.GetImageAndResizeTK("CapturedImages/capture.png", 0.2)
capture = imageManager.GetImageTK(imageManager.GetEmptyImage())
imageLabel = Label(image=capture)

#contourImage = imageManager.GetImageAndResizeTK("CapturedImages/contourImage.png", (0.2))
contourImage = imageManager.GetImageTK(imageManager.GetEmptyImage())
imageLabel2 = Label(image=contourImage)

imageLabel.grid(row=0, column=0)
imageLabel2.grid(row=0, column=2)

    

def RefreshCapturedImage(capturedImage):
    global capture
    capture = capturedImage
    imageLabel.configure(image = capture)

def RefreshProcessedImage(processedImage):
    global contourImage
    contourImage = processedImage
    imageLabel2.configure(image=contourImage)

def TakeAndMeasureImage():
    capturedimage = captureImage.CaptureImage()
    processedImage = imageProcessing.ProcessImage(capturedimage)

    pt.StartTimer()

    RefreshCapturedImage(imageManager.PILToTKAndResize(capturedimage, 0.2))
    RefreshProcessedImage(imageManager.CV2ToTKAndResize(processedImage, 0.2))

    pt.StopTimer("Refreshed images")

def EnableButtonWhenRelatedTaskIsFinished(threadToTrack, buttonToEnable):
    threadToTrack.join()
    buttonToEnable["state"] = "normal"

def DisableButtonWhenRelatedTaskIsRunning(threadToRun, button):
    button["state"] = "disabled"
    threadToRun.start()
    threading.Thread(target=EnableButtonWhenRelatedTaskIsFinished, args=(threadToRun, button)).start()


captureThread = threading.Thread(target=TakeAndMeasureImage)

previewButton = Button(root, text="Preview", command=captureImage.Preview)
captureButton = Button(root, text="Capture", command=captureImage.CaptureImage)
imageProcessButton = Button(root, text="Process Image", command=imageProcessing.ProcessImage)
captureAndProcessButton = Button(root, text="Process & capture", command= lambda: DisableButtonWhenRelatedTaskIsRunning(captureThread, captureAndProcessButton))

previewButton.grid(row=2, column=0)
captureButton.grid(row=3, column=0)
imageProcessButton.grid(row=4, column=0)
captureAndProcessButton.grid(row=5, column=0)

root.mainloop();