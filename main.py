from tkinter import *

import CaptureImage as captureImage
import ImageProcessing as imageProcessing

root = Tk()

captureButton = Button(root, text="Capture", command=captureImage.CaptureImage)
imageProcessButton = Button(root, text="Process Image", command=imageProcessing.ProcessImage)
imageProcessButton = Button(root, text="Process Image", command=imageProcessing.ProcessImage)

captureButton.grid(row=0, column=0)
imageProcessButton.grid(row=0, column=1)

root.mainloop();