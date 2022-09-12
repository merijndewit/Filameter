from tkinter import *


import CaptureImage as captureImage
import ImageProcessing as imageProcessing
import ImageManager as imageManager




root = Tk()



capture = imageManager.GetImageTK("CapturedImages/capture.png", (265, 159))
imageLabel = Label(image=capture)

thresholdImage = imageManager.GetImageTK("CapturedImages/processedImage.png", (265, 159))
imageLabel1 = Label(image=thresholdImage)

contourImage = imageManager.GetImageTK("CapturedImages/contourImage.png", (265, 159))
imageLabel2 = Label(image=contourImage)


imageLabel.grid(row=0, column=0)
imageLabel1.grid(row=0, column=1)
imageLabel2.grid(row=0, column=2)

def Clicked():
    global capture
    global thresholdImage
    global contourImage
    #global imageLabel

    capture = imageManager.GetImageTK("CapturedImages/capture.png", (265, 159))
    imageLabel.configure(image = capture)

    thresholdImage = imageManager.GetImageTK("CapturedImages/processedImage.png", (265, 159))
    imageLabel1.configure(image=thresholdImage)

    contourImage = imageManager.GetImageTK("CapturedImages/contourImage.png", (265, 159))
    imageLabel2.configure(image=contourImage)

previewButton = Button(root, text="Preview", command=captureImage.Preview)
captureButton = Button(root, text="Capture", command=captureImage.CaptureImage)
imageProcessButton = Button(root, text="Process Image", command=imageProcessing.ProcessImage)
refreshImages = Button(root, text="Refresh Image", command=Clicked)
previewButton.grid(row=2, column=0)
captureButton.grid(row=3, column=0)
imageProcessButton.grid(row=4, column=0)
refreshImages.grid(row=5, column=0)

root.mainloop();