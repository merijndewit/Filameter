from ast import arguments
from tkinter import *

import customtkinter
import CaptureImage as captureImage
import ImageProcessing as imageProcessing
import ImageManager as imageManager
import PerformanceTimer as pt
import threading

root = customtkinter.CTk()
root.geometry("800x480")
root.configure(bg='#121212')

imageFrame = customtkinter.CTkFrame(master=root,
                               width=800,
                               height=200,
                               corner_radius=4,
                               fg_color="#1E1E1E")
imageFrame.grid(row=0, column=0, padx=(10, 10), pady=(10, 10))


#capture = imageManager.GetImageTK(imageManager.GetEmptyImage())
imageLabel = customtkinter.CTkLabel(master=imageFrame, width=760, height=190, bg_color="#292929", corner_radius=0, text="")

imageLabel.grid(row=0, column=0, padx=(10, 10), pady=(10, 10))

buttonColor = "#F5BEE0"
buttonHoverColor = "#EAC3D6"

def RefreshProcessedImage(processedImage):
    global contourImage
    contourImage = processedImage
    imageLabel.configure(image=contourImage)

def TakeAndMeasureImage():
    capturedimage = captureImage.CaptureImage()
    processedImage = imageProcessing.ProcessImage(capturedimage)

    pt.StartTimer()

    RefreshProcessedImage(imageManager.CV2ToTKAndResize(processedImage, 0.38))

    pt.StopTimer("Refreshed images")

def EnableButtonWhenRelatedTaskIsFinished(threadToTrack, buttonToEnable):
    threadToTrack.join()
    buttonToEnable["state"] = "normal"

def DisableButtonWhenRelatedTaskIsRunning(threadToRun, button):
    button["state"] = "disabled"
    threadToRun.start()
    threading.Thread(target=EnableButtonWhenRelatedTaskIsFinished, args=(threadToRun, button)).start()

captureAndProcessButton = customtkinter.CTkButton(root, text="Process \n & \n capture", fg_color=buttonColor, hover_color=buttonHoverColor, text_font=("Arial Baltic", 11), width=80, height=65,command= lambda: DisableButtonWhenRelatedTaskIsRunning(threading.Thread(target=TakeAndMeasureImage), captureAndProcessButton))
captureAndProcessButton.grid(row=2, column=0, padx=(10, 0), pady=(10, 0))

previewButton = customtkinter.CTkButton(master=root, text="Preview",  fg_color=buttonColor, hover_color=buttonHoverColor, text_font=("", 11), width=80, height=35, command=captureImage.Preview)
previewButton.grid(row=3, column=0, padx=(10, 0), pady=(10, 0))
#button.place(relx=0.5, rely=0.5, anchor=CENTER)

root.mainloop();