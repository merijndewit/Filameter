from ast import arguments
from tkinter import *

import customtkinter
import CaptureImage as captureImage
import ImageProcessing as imageProcessing
import ImageManager as imageManager
import PerformanceTimer as pt
import threading

buttonColor = "#F5BEE0"
buttonHoverColor = "#F9DCEE"

filamentViewFrame = None
buttonFrame = None
measurementFrame = None

def TakeAndMeasureImage():
    capturedimage = captureImage.CaptureImage()
    processedImage = imageProcessing.ProcessImage(capturedimage)

    pt.StartTimer()

    filamentViewFrame.RefreshProcessedImage(imageManager.CV2ToTKAndResize(processedImage, 0.34))

    pt.StopTimer("Refreshing images")

class ButtonHelper():
    @staticmethod
    def EnableButtonWhenRelatedTaskIsFinished(threadToTrack, buttonToEnable):
        threadToTrack.join()
        buttonToEnable.configure(state=NORMAL)
    @staticmethod
    def DisableButtonWhenRelatedTaskIsRunning(threadToRun, button):
        button.configure(state=DISABLED)
        threadToRun.start()
        threading.Thread(target=ButtonHelper.EnableButtonWhenRelatedTaskIsFinished, args=(threadToRun, button)).start()


class FilamentViewFrame(customtkinter.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        customtkinter.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.configure( width=800,
                        height=200,
                        corner_radius=4,
                        fg_color="#1E1E1E")
        self.grid(row=0, column=0, padx=(60, 60), pady=(10, 5))
        self.imageLabel = customtkinter.CTkLabel(master=self, width=680, height=170, bg_color="#292929", corner_radius=0, text="")

        self.imageLabel.grid(row=0, column=0, padx=(10, 10), pady=(10, 10))

    def RefreshProcessedImage(self,processedImage):
        global contourImage
        contourImage = processedImage
        self.imageLabel.configure(image=contourImage)

class ButtonFrame(customtkinter.CTkFrame):  
    def __init__(self, parent, *args, **kwargs):
        customtkinter.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.configure( width=150,
                        height=200,
                        corner_radius=4,
                        fg_color="#1E1E1E")

        self.grid(row=1, column=0, padx=(10, 0), pady=(5, 0), sticky=W)

        self.headerLabel = customtkinter.CTkLabel(master=self, text="Single Actions", text_color="#ffffff" )
        self.headerLabel.grid(row=0, column=0, padx=(2, 2), pady=(2, 0))

        self.captureAndProcessButton = customtkinter.CTkButton(master=self, text="Process \n & \n capture", fg_color=buttonColor, hover_color=buttonHoverColor, text_font=("Arial Baltic", 11), width=80, height=65,command= lambda: ButtonHelper.DisableButtonWhenRelatedTaskIsRunning(threading.Thread(target=TakeAndMeasureImage), self.captureAndProcessButton))
        self.captureAndProcessButton.grid(row=1, column=0, padx=(10, 10), pady=(2, 5))

        self.previewButton = customtkinter.CTkButton(master=self, text="Preview",  fg_color=buttonColor, hover_color=buttonHoverColor, text_font=("", 11), width=80, height=55, command=captureImage.Preview)
        self.previewButton.grid(row=2, column=0, padx=(10, 10), pady=(5, 10))

class ControlPad(customtkinter.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        customtkinter.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.configure( width=150,
                        height=200,
                        corner_radius=4,
                        fg_color="#1E1E1E")

        self.grid(row=1, column=0, padx=(10, 30), pady=(5, 0), sticky=E)

        self.headerLabel = customtkinter.CTkLabel(master=self, text="Control", text_color="#ffffff" )
        self.headerLabel.grid(row=0, column=0, padx=(2, 2), pady=(2, 0))

        self.addButton = customtkinter.CTkButton(master=self, text="+", fg_color=buttonColor, hover_color=buttonHoverColor, text_font=("", 16), width=50, height=50)
        self.addButton.grid(row=1, column=0, padx=(10, 10), pady=(2, 5))

        self.subtractButton = customtkinter.CTkButton(master=self, text="-",  fg_color=buttonColor, hover_color=buttonHoverColor, text_font=("", 16), width=50, height=50)
        self.subtractButton.grid(row=2, column=0, padx=(10, 10), pady=(5, 10))


    def AddNumberOfCuts(self, numberOfCutsToAdd):
        numberOfCutsToAdd

        


if __name__ == "__main__":
    root = customtkinter.CTk()
    root.geometry("800x480")
    root.configure(bg='#121212')
    filamentViewFrame = FilamentViewFrame(root)
    buttonFrame = ButtonFrame(root)
    measurementFrame = ControlPad(root)

    root.mainloop();