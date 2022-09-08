from tkinter import *

import CaptureImage as captureImage
import ImageProcessing as imageProcessing

root = Tk()

previewButton = Button(root, text="Preview", command=captureImage.Preview)
captureButton = Button(root, text="Capture", command=captureImage.CaptureImage)
imageProcessButton = Button(root, text="Process Image", command=imageProcessing.ProcessImage)

previewButton.grid(row=0, column=0)
captureButton.grid(row=1, column=0)
imageProcessButton.grid(row=2, column=0)

root.mainloop();