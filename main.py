from ast import arguments
from cgitb import text
from tkinter import *

import customtkinter
import CaptureImage as captureImage
import ImageProcessing as imageProcessing
import ImageManager as imageManager
import PerformanceTimer as pt
import threading
import time

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

        self.captureAndProcessButton = customtkinter.CTkButton(master=self, text="Process \n & \n capture", fg_color=parent.buttonColor, hover_color=parent.buttonHoverColor, text_font=("Arial Baltic", 11), width=80, height=65,command= lambda: ButtonHelper.DisableButtonWhenRelatedTaskIsRunning(threading.Thread(target=parent.TakeAndMeasureImage), self.captureAndProcessButton))
        self.captureAndProcessButton.grid(row=1, column=0, padx=(10, 10), pady=(2, 5))

        self.previewButton = customtkinter.CTkButton(master=self, text="Preview",  fg_color=parent.buttonColor, hover_color=parent.buttonHoverColor, text_font=("", 11), width=80, height=55, command=captureImage.Preview)
        self.previewButton.grid(row=2, column=0, padx=(10, 10), pady=(5, 10))

class ControlPad(customtkinter.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        customtkinter.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.configure( width=150,
                        height=200,
                        corner_radius=4,
                        fg_color="#1E1E1E")

        self.grid(row=1, column=0, padx=(10, 30), pady=(5, 0), sticky=NE)

        self.headerLabel = customtkinter.CTkLabel(master=self, text="Control", text_color="#ffffff" )
        self.headerLabel.grid(row=0, column=0, padx=(2, 2), pady=(2, 0))

        self.addButton = customtkinter.CTkButton(master=self, text="+", fg_color=parent.buttonColor, hover_color=parent.buttonHoverColor, text_font=("", 16), width=50, height=50, command= lambda: self.parent.settingsFrame.AddSelectedValue(1))
        self.addButton.grid(row=1, column=0, padx=(10, 10), pady=(2, 5))

        self.subtractButton = customtkinter.CTkButton(master=self, text="-",  fg_color=parent.buttonColor, hover_color=parent.buttonHoverColor, text_font=("", 16), width=50, height=50, command= lambda: self.parent.settingsFrame.AddSelectedValue(-1))
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

    def AddValue(self, value):
        self.value += value

class SettingsFrame(customtkinter.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        customtkinter.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.configure( width=150,
                        height=200,
                        corner_radius=4,
                        fg_color="#1E1E1E")

        self.grid(row=1, column=0, padx=(200, 30), pady=(5, 0), sticky=NW)

        self.selectedButton = None

        self.headerLabel = customtkinter.CTkLabel(master=self, text="Settings", text_color="#ffffff" )
        self.headerLabel.grid(row=0, column=0, padx=(2, 2), pady=(2, 0))

        self.numberOfMeasurementsButton = customtkinter.CTkButton(master=self, fg_color="#292929", hover_color="#292929", text_font=("", 11), text_color="#ffffff", width=90, height=40)
        self.numberOfMeasurementsButton.grid(row=1, column=0, padx=(10, 10), pady=(2, 5))
        self.numberOfMeasurementsSetting = SettingsButton(self.numberOfMeasurementsButton, "No of M. ", 4)
        self.numberOfMeasurementsButton.configure(command=lambda: self.Select(self.numberOfMeasurementsSetting))
        self.numberOfMeasurementsSetting.UpdateTextValue()

        self.measureBorderOffsetButton = customtkinter.CTkButton(master=self, text="M. border offset", fg_color="#292929", hover_color="#292929", text_font=("", 11), text_color="#ffffff", width=90, height=40)
        self.measureBorderOffsetButton.grid(row=2, column=0, padx=(10, 10), pady=(2, 5))
        self.measureBorderOffsetButtonSetting = SettingsButton(self.measureBorderOffsetButton, "M. border offset ", 200)
        self.measureBorderOffsetButton.configure(command=lambda: self.Select(self.measureBorderOffsetButtonSetting))
        self.measureBorderOffsetButtonSetting.UpdateTextValue()

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
        
        self.selectedButton.AddValue(value)
        self.selectedButton.UpdateTextValue()

    def GetNumberOfMeasurements(self):
        return self.numberOfMeasurementsSetting.value

    def GetBorderOffset(self):
        return self.measureBorderOffsetButtonSetting.value


class RecordPad(customtkinter.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        customtkinter.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.configure( width=150,
                        height=200,
                        corner_radius=4,
                        fg_color="#1E1E1E")

        self.grid(row=1, column=0, padx=(320, 30), pady=(5, 0), sticky=N)

        self.headerLabel = customtkinter.CTkLabel(master=self, text="Record", text_color="#ffffff" )
        self.headerLabel.grid(row=0, column=0, padx=(2, 2), pady=(2, 0))

        self.addButton = customtkinter.CTkButton(master=self, text="Start", fg_color=parent.buttonColor, hover_color=parent.buttonHoverColor, text_font=("", 11), width=55, height=35, command= lambda: self.parent.StartRecording())
        self.addButton.grid(row=1, column=0, padx=(5, 2), pady=(2, 5), sticky=W)

        self.subtractButton = customtkinter.CTkButton(master=self, text="Stop",  fg_color=parent.buttonColor, hover_color=parent.buttonHoverColor, text_font=("", 11), width=55, height=35, command= lambda: self.parent.StopRecording())
        self.subtractButton.grid(row=1, column=0, padx=(2, 5), pady=(5, 10), sticky=E)

class Main(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        customtkinter.CTk.__init__(self, *args, **kwargs)
        self.geometry("800x480")
        self.configure(bg='#121212')

        self.buttonColor = "#F5BEE0"
        self.buttonHoverColor = "#F9DCEE"

        self.recordingThread = None
        self.recording = False

        self.lastAverageReading = 0

        self.filamentViewFrame = FilamentViewFrame(self)
        self.buttonFrame = ButtonFrame(self)
        self.settingsFrame = SettingsFrame(self)
        self.controlPad = ControlPad(self)
        self.recordPad = RecordPad(self)
        self.mainloop();

    def TakeAndMeasureImage(self):
        capturedimage = captureImage.CaptureImage()
        processedImage, self.lastAverageReading = imageProcessing.ProcessImage(capturedimage, self.settingsFrame.GetNumberOfMeasurements(), self.settingsFrame.GetBorderOffset())
        print("Last average reading was: " + str(self.lastAverageReading))
        pt.StartTimer()

        self.filamentViewFrame.RefreshProcessedImage(imageManager.CV2ToTKAndResize(processedImage, 0.34))

        pt.StopTimer("Refreshing images")

    def StartRecording(self):
        print("start recording")
        self.recording = True
        self.recordingThread = threading.Thread(target= lambda: self.Record(0)).start()

    def StopRecording(self):
        self.recording = False
        #self.recordingThread.join()
        print("stop recording")

    def Record(self, delaySec):
        while self.recording:
            self.TakeAndMeasureImage()
            time.sleep(delaySec)

if __name__ == "__main__":
    Main()