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
imageFrame.grid(row=0, column=0, padx=(10, 10), pady=(10, 5))

buttonFrame = customtkinter.CTkFrame(master=root,
                               width=150,
                               height=200,
                               corner_radius=4,
                               fg_color="#1E1E1E")
buttonFrame.grid(row=1, column=0, padx=(10, 0), pady=(5, 0), sticky=W)

#capture = imageManager.GetImageTK(imageManager.GetEmptyImage())
imageLabel = customtkinter.CTkLabel(master=imageFrame, width=760, height=190, bg_color="#292929", corner_radius=0, text="")

imageLabel.grid(row=0, column=0, padx=(10, 10), pady=(10, 10))

buttonColor = "#F5BEE0"
buttonHoverColor = "#F9DCEE"

def RefreshProcessedImage(processedImage):
    global contourImage
    contourImage = processedImage
    imageLabel.configure(image=contourImage)

def TakeAndMeasureImage():
    capturedimage = captureImage.CaptureImage()
    processedImage = imageProcessing.ProcessImage(capturedimage)

    pt.StartTimer()

    RefreshProcessedImage(imageManager.CV2ToTKAndResize(processedImage, 0.38))

    pt.StopTimer("Refreshing images")

def EnableButtonWhenRelatedTaskIsFinished(threadToTrack, buttonToEnable):
    threadToTrack.join()
    buttonToEnable.configure(state=NORMAL)

def DisableButtonWhenRelatedTaskIsRunning(threadToRun, button):
    button.configure(state=DISABLED)
    threadToRun.start()
    threading.Thread(target=EnableButtonWhenRelatedTaskIsFinished, args=(threadToRun, button)).start()

captureAndProcessButton = customtkinter.CTkButton(master=buttonFrame, text="Process \n & \n capture", fg_color=buttonColor, hover_color=buttonHoverColor, text_font=("Arial Baltic", 11), width=80, height=65,command= lambda: DisableButtonWhenRelatedTaskIsRunning(threading.Thread(target=TakeAndMeasureImage), captureAndProcessButton))
captureAndProcessButton.grid(row=0, column=0, padx=(10, 10), pady=(10, 5))

previewButton = customtkinter.CTkButton(master=buttonFrame, text="Preview",  fg_color=buttonColor, hover_color=buttonHoverColor, text_font=("", 11), width=80, height=55, command=captureImage.Preview)
previewButton.grid(row=1, column=0, padx=(10, 10), pady=(5, 10))
#button.place(relx=0.5, rely=0.5, anchor=CENTER)

root.mainloop();