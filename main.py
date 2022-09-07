from tkinter import *
import os

import CaptureImage as captureImage

root = Tk()

captureButton = Button(root, text="Capture", command=captureImage.CaptureImage)

captureButton.grid(row=0, column=0)

root.mainloop();