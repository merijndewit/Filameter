from tkinter import *

import CaptureImage as captureImage
import ImageProcessing as imageProcessing
import ImageManager as imageManager
import PerformanceTimer as pt

root = Tk()

capture = imageManager.GetImageAndResizeTK("CapturedImages/capture.png", 0.2)
imageLabel = Label(image=capture)

contourImage = imageManager.GetImageAndResizeTK("CapturedImages/contourImage.png", (0.2))
imageLabel2 = Label(image=contourImage)

imageLabel.grid(row=0, column=0)
imageLabel2.grid(row=0, column=2)

def RefreshImages():
    global capture
    global contourImage
    pt.StartTimer()
    capture = imageManager.GetImageAndResizeTK("CapturedImages/capture.png", 0.2)
    imageLabel.configure(image = capture)

    contourImage = imageManager.GetImageAndResizeTK("CapturedImages/contourImage.png", 0.2)
    imageLabel2.configure(image=contourImage)
    pt.StopTimer("Refreshing image")

previewButton = Button(root, text="Preview", command=captureImage.Preview)
captureButton = Button(root, text="Capture", command=captureImage.CaptureImage)
imageProcessButton = Button(root, text="Process Image", command=imageProcessing.ProcessImage)
refreshImages = Button(root, text="Refresh Image", command=RefreshImages)
previewButton.grid(row=2, column=0)
captureButton.grid(row=3, column=0)
imageProcessButton.grid(row=4, column=0)
refreshImages.grid(row=5, column=0)

root.mainloop();