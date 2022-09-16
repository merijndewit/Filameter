from ast import arguments
from cgitb import text
from tkinter import *

import customtkinter
import CaptureImage as captureImage
import ImageProcessing as imageProcessing
import ImageManager as imageManager
import PerformanceTimer as pt
import threading

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


class FilamentViewFrame():
    def __init__(self, parent, *args, **kwargs):
        self.frame = customtkinter.CTkFrame(master=parent.root)
        self.parent = parent
        self.frame.configure( width=800,
                        height=200,
                        corner_radius=4,
                        fg_color="#1E1E1E")
        self.frame.grid(row=0, column=0, padx=(60, 60), pady=(10, 5))
        self.imageLabel = customtkinter.CTkLabel(master=self.frame, width=680, height=170, bg_color="#292929", corner_radius=0, text="")

        self.imageLabel.grid(row=0, column=0, padx=(10, 10), pady=(10, 10))

    def RefreshProcessedImage(self,processedImage):
        global contourImage
        contourImage = processedImage
        self.imageLabel.configure(image=contourImage)

class ButtonFrame():  
    def __init__(self, parent, *args, **kwargs):
        self.frame = customtkinter.CTkFrame(master=parent.root)
        self.parent = parent
        self.frame.configure( width=150,
                        height=200,
                        corner_radius=4,
                        fg_color="#1E1E1E")

        self.frame.grid(row=1, column=0, padx=(10, 0), pady=(5, 0), sticky=W)

        self.headerLabel = customtkinter.CTkLabel(master=self.frame, text="Single Actions", text_color="#ffffff" )
        self.headerLabel.grid(row=0, column=0, padx=(2, 2), pady=(2, 0))

        self.captureAndProcessButton = customtkinter.CTkButton(master=self.frame, text="Process \n & \n capture", fg_color=parent.buttonColor, hover_color=parent.buttonHoverColor, text_font=("Arial Baltic", 11), width=80, height=65,command= lambda: ButtonHelper.DisableButtonWhenRelatedTaskIsRunning(threading.Thread(target=parent.TakeAndMeasureImage), self.captureAndProcessButton))
        self.captureAndProcessButton.grid(row=1, column=0, padx=(10, 10), pady=(2, 5))

        self.previewButton = customtkinter.CTkButton(master=self.frame, text="Preview",  fg_color=parent.buttonColor, hover_color=parent.buttonHoverColor, text_font=("", 11), width=80, height=55, command=captureImage.Preview)
        self.previewButton.grid(row=2, column=0, padx=(10, 10), pady=(5, 10))

class ControlPad():
    def __init__(self, parent, *args, **kwargs):
        self.frame = customtkinter.CTkFrame(master=parent.root)
        self.parent = parent
        self.frame.configure( width=150,
                        height=200,
                        corner_radius=4,
                        fg_color="#1E1E1E")

        self.frame.grid(row=1, column=0, padx=(10, 30), pady=(5, 0), sticky=E)

        self.headerLabel = customtkinter.CTkLabel(master=self.frame, text="Control", text_color="#ffffff" )
        self.headerLabel.grid(row=0, column=0, padx=(2, 2), pady=(2, 0))

        self.addButton = customtkinter.CTkButton(master=self.frame, text="+", fg_color=parent.buttonColor, hover_color=parent.buttonHoverColor, text_font=("", 16), width=50, height=50, command= lambda: self.parent.AddSelectedValueToSettingFrame(1))
        self.addButton.grid(row=1, column=0, padx=(10, 10), pady=(2, 5))

        self.subtractButton = customtkinter.CTkButton(master=self.frame, text="-",  fg_color=parent.buttonColor, hover_color=parent.buttonHoverColor, text_font=("", 16), width=50, height=50, command= lambda: self.parent.AddSelectedValueToSettingFrame(-1))
        self.subtractButton.grid(row=2, column=0, padx=(10, 10), pady=(5, 10))

class SettingsButton():
    def __init__(self, ctkButton, text, value):
        self.ctkButton = ctkButton
        self.text = text
        self.value = value

    def Select(self):
        self.ctkButton.configure(fg_color="#7C98B3", hover_color="#7C98B3")

    def UnSelect(self):
        self.ctkButton.configure(fg_color="#292929", hover_color="#292929")

    def UpdateTextValue(self):
        self.ctkButton.configure(text=self.text + str(self.value))

    def ChangeValue(self, value):
        self.value = value

class SettingsFrame():
    def __init__(self, parent, *args, **kwargs):
        self.frame = customtkinter.CTkFrame(master=parent.root)
        self.parent = parent
        self.frame.configure( width=150,
                        height=200,
                        corner_radius=4,
                        fg_color="#1E1E1E")

        self.frame.grid(row=1, column=0, padx=(200, 30), pady=(5, 0), sticky=W)

        self.selectedButton = None

        self.numberOfMeasurements = 4

        self.headerLabel = customtkinter.CTkLabel(master=self.frame, text="Settings", text_color="#ffffff" )
        self.headerLabel.grid(row=0, column=0, padx=(2, 2), pady=(2, 0))

        self.numberOfMeasurementsButton = customtkinter.CTkButton(master=self.frame, fg_color="#292929", hover_color="#292929", text_font=("", 11), text_color="#ffffff", width=90, height=40)
        self.numberOfMeasurementsButton.grid(row=1, column=0, padx=(10, 10), pady=(2, 5))
        self.numberOfMeasurementsSetting = SettingsButton(self.numberOfMeasurementsButton, "No of measurements ", 4)
        self.numberOfMeasurementsButton.configure(command=lambda: self.Select(self.numberOfMeasurementsSetting))
        self.numberOfMeasurementsSetting.UpdateTextValue()

        self.test1 = customtkinter.CTkButton(master=self.frame, text="test1", fg_color="#292929", hover_color="#292929", text_font=("", 11), text_color="#ffffff", width=90, height=40)
        self.test1.grid(row=2, column=0, padx=(10, 10), pady=(2, 5))
        self.test1Setting = SettingsButton(self.test1, "test1 ", 4)
        self.test1.configure(command=lambda: self.Select(self.test1Setting))
        self.test1Setting.UpdateTextValue()

        self.test2 = customtkinter.CTkButton(master=self.frame, text="test2", fg_color="#292929", hover_color="#292929", text_font=("", 11), text_color="#ffffff", width=90, height=40)
        self.test2.grid(row=3, column=0, padx=(10, 10), pady=(2, 5))
        self.test2Setting = SettingsButton(self.test2, "test2 ", 4)
        self.test2.configure(command=lambda: self.Select(self.test2Setting))
        self.test2Setting.UpdateTextValue()

    def Select(self, selectedButton):
        if selectedButton == self.selectedButton:
            selectedButton.UnSelect()
            self.selectedButton = None
            return
        if self.selectedButton is not None:
            self.selectedButton.UnSelect()
        self.selectedButton = selectedButton
        selectedButton.Select()

    def AddSelectedValue(self, value):

        if self.selectedButton == None:
            return
        print("adad")
        newValue = self.selectedButton.value + value
        

        self.selectedButton.ChangeValue(newValue)
        self.selectedButton.UpdateTextValue()

class Main():
    def __init__(self, *args, **kwargs):
        self.root = customtkinter.CTk()
        self.root.geometry("800x480")
        self.root.configure(bg='#121212')

        self.buttonColor = "#F5BEE0"
        self.buttonHoverColor = "#F9DCEE"

        self.filamentViewFrame = FilamentViewFrame(self)
        self.buttonFrame = ButtonFrame(self)
        self.settingsFrame = SettingsFrame(self)
        self.controlPad = ControlPad(self)
        self.root.mainloop();

    def TakeAndMeasureImage(self):
        capturedimage = captureImage.CaptureImage()
        processedImage = imageProcessing.ProcessImage(capturedimage)

        pt.StartTimer()

        self.filamentViewFrame.RefreshProcessedImage(imageManager.CV2ToTKAndResize(processedImage, 0.34))

        pt.StopTimer("Refreshing images")

    def AddSelectedValueToSettingFrame(self, value):
        self.settingsFrame.AddSelectedValue(value)
        self.root.update_idletasks()


if __name__ == "__main__":
    Main()