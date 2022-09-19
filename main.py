from ast import arguments
from cgitb import text
from tkinter import *
from enum import Enum

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
        self.configure( width=620,
                        height=180,
                        corner_radius=4,
                        fg_color="#1E1E1E")
        self.grid(row=0, column=0, padx=(10, 10), pady=(10, 5), sticky=W)
        self.imageLabel = customtkinter.CTkLabel(master=self, width=600, height=150, bg_color="#292929", corner_radius=0, text="")

        self.imageLabel.grid(row=0, column=0, padx=(10, 10), pady=(10, 10))

    def RefreshProcessedImage(self,processedImage):
        global contourImage
        contourImage = processedImage
        self.imageLabel.configure(image=contourImage)

class FilamentInfo(customtkinter.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        customtkinter.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.configure( width=150,
                        height=200,
                        corner_radius=4,
                        fg_color="#1E1E1E")
        self.grid(row=0, column=0, padx=(640, 10), pady=(10, 5), sticky=NE)

        self.headerLabel = customtkinter.CTkLabel(master=self, text="Filament Info", text_color="#ffffff", text_font='Helvetica 11 bold')
        self.headerLabel.grid(row=0, column=0, padx=(2, 2), pady=(2, 0))

        self.averageText = customtkinter.CTkLabel(master=self, text="Avg dia: ", text_color="#ffffff")
        self.averageText.grid(row=1, column=0, padx=(2, 2), pady=(2, 0))

    def SetAverageTextValue(self, value):
        self.averageText.configure(text="Avg dia: " + str(round(value, 3)) + "mm")



class ButtonFrame(customtkinter.CTkFrame):  
    def __init__(self, parent, *args, **kwargs):
        customtkinter.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.configure( width=150,
                        height=200,
                        corner_radius=4,
                        fg_color="#1E1E1E")

        self.grid(row=1, column=0, padx=(10, 0), pady=(5, 0), sticky=W)

        self.headerLabel = customtkinter.CTkLabel(master=self, text="Single Actions", text_color="#ffffff", text_font='Helvetica 11 bold')
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

        self.grid(row=1, column=0, padx=(600, 5), pady=(5, 0), sticky=NE)

        self.headerLabel = customtkinter.CTkLabel(master=self, text="Control", text_color="#ffffff", text_font='Helvetica 11 bold')
        self.headerLabel.grid(row=0, column=0, padx=(2, 2), pady=(2, 0))

        self.addButton = customtkinter.CTkButton(master=self, text="+", fg_color=parent.buttonColor, hover_color=parent.buttonHoverColor, text_font=("", 16), width=50, height=50, command= lambda: self.parent.settingsFrame.AddSelectedValue(1))
        self.addButton.grid(row=1, column=0, padx=(10, 10), pady=(2, 5))

        self.subtractButton = customtkinter.CTkButton(master=self, text="-",  fg_color=parent.buttonColor, hover_color=parent.buttonHoverColor, text_font=("", 16), width=50, height=50, command= lambda: self.parent.settingsFrame.AddSelectedValue(-1))
        self.subtractButton.grid(row=2, column=0, padx=(10, 10), pady=(5, 10))

class SettingType(Enum):
    NUMBEROFMEASUREMENTS = 1
    BORDEROFFSET = 2
    PIXELSPERMM = 3

class Setting():
    def __init__(self, value, settingType):
        self.value = value
        self.type = settingType

    def GetValue(self):
        return self.value

    def GetValueInt(self):
        return int(self.value)
    
    def GetValueFloat(self):
        return float(self.value)

    def Set(self, value):
        self.value = value

    def Add(self, value):
        self.value += value


class Settings():
    def __init__(self):
        self.settings = []
        self.CreateSetting(4, SettingType.NUMBEROFMEASUREMENTS)
        self.CreateSetting(200, SettingType.BORDEROFFSET)
        self.CreateSetting(157, SettingType.PIXELSPERMM)

    def CreateSetting(self, value, settingType):
        newSetting = Setting(value, settingType)
        self.settings.append(newSetting)

    def GetSetting(self, settingType):
        for i in range(len(self.settings)):
            if self.settings[i].type == settingType:
                return self.settings[i]

class SettingsButton():
    def __init__(self, ctkButton, text, settingType, main):
        self.ctkButton = ctkButton
        self.text = text
        self.settingType = settingType
        self.main = main

    def Select(self):
        self.ctkButton.configure(fg_color="#7C98B3", hover_color="#7C98B3")

    def UnSelect(self):
        self.ctkButton.configure(fg_color="#292929", hover_color="#292929")

    def SetTextValue(self, value):
        self.ctkButton.configure(text=self.text + str(value))

    def UpdateTextValueFromSetting(self):
        setting = self.main.settings.GetSetting(self.settingType)

        self.ctkButton.configure(text=self.text + str(setting.GetValue()))

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

        self.headerLabel = customtkinter.CTkLabel(master=self, text="Settings", text_color="#ffffff", text_font='Helvetica 11 bold')
        self.headerLabel.grid(row=0, column=0, padx=(2, 2), pady=(2, 0))

        self.numberOfMeasurementsButton = customtkinter.CTkButton(master=self, fg_color="#292929", hover_color="#292929", text_font=("", 11), text_color="#ffffff", width=90, height=40)
        self.numberOfMeasurementsButton.grid(row=1, column=0, padx=(10, 10), pady=(2, 5))
        self.numberOfMeasurementsSetting = SettingsButton(self.numberOfMeasurementsButton, "No of M. ", SettingType.NUMBEROFMEASUREMENTS, self.parent)
        self.numberOfMeasurementsButton.configure(command=lambda: self.Select(self.numberOfMeasurementsSetting))
        self.numberOfMeasurementsSetting.UpdateTextValueFromSetting()

        self.measureBorderOffsetButton = customtkinter.CTkButton(master=self, text="M. border offset", fg_color="#292929", hover_color="#292929", text_font=("", 11), text_color="#ffffff", width=90, height=40)
        self.measureBorderOffsetButton.grid(row=2, column=0, padx=(10, 10), pady=(2, 5))
        self.measureBorderOffsetButtonSetting = SettingsButton(self.measureBorderOffsetButton, "M. border offset ", SettingType.BORDEROFFSET, self.parent)
        self.measureBorderOffsetButton.configure(command=lambda: self.Select(self.measureBorderOffsetButtonSetting))
        self.measureBorderOffsetButtonSetting.UpdateTextValueFromSetting()

        self.pixelsPerMMButton = customtkinter.CTkButton(master=self, text="pixels per mm", fg_color="#292929", hover_color="#292929", text_font=("", 11), text_color="#ffffff", width=90, height=40)
        self.pixelsPerMMButton.grid(row=3, column=0, padx=(10, 10), pady=(2, 5))
        self.pixelsPerMMButtonSetting = SettingsButton(self.pixelsPerMMButton, "pixels per mm ", SettingType.PIXELSPERMM, self.parent)
        self.pixelsPerMMButton.configure(command=lambda: self.Select(self.pixelsPerMMButtonSetting))
        self.pixelsPerMMButtonSetting.UpdateTextValueFromSetting()


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
        setting = self.parent.settings.GetSetting(self.selectedButton.settingType)
        
        setting.Add(value)
        self.selectedButton.UpdateTextValueFromSetting()


class RecordPad(customtkinter.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        customtkinter.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.configure( width=150,
                        height=200,
                        corner_radius=4,
                        fg_color="#1E1E1E")

        self.grid(row=1, column=0, padx=(320, 30), pady=(5, 0), sticky=N)

        self.headerLabel = customtkinter.CTkLabel(master=self, text="Record", text_color="#ffffff", text_font='Helvetica 11 bold')
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

        #settings
        self.settings = Settings()

        #frames
        self.filamentViewFrame = FilamentViewFrame(self)
        self.buttonFrame = ButtonFrame(self)
        self.settingsFrame = SettingsFrame(self)
        self.controlPad = ControlPad(self)
        self.recordPad = RecordPad(self)
        self.filamentInfo= FilamentInfo(self)

        self.imageProcessing = imageProcessing.ImageProcessing()

        self.mainloop();

    def TakeAndMeasureImage(self):
        capturedimage = captureImage.CaptureImage()
        processedImage, self.lastAverageReading = self.imageProcessing.ProcessImage(capturedimage, self.settings.GetSetting(SettingType.NUMBEROFMEASUREMENTS).GetValueInt(), self.settings.GetSetting(SettingType.BORDEROFFSET).GetValueInt(), self.settings.GetSetting(SettingType.PIXELSPERMM).GetValueFloat())
        self.filamentInfo.SetAverageTextValue(self.lastAverageReading)
        pt.StartTimer()

        self.filamentViewFrame.RefreshProcessedImage(imageManager.CV2ToTKAndResize(processedImage, 0.30))

        pt.StopTimer("Refreshing images")

    def StartRecording(self):
        self.recording = True
        self.recordingThread = threading.Thread(target= lambda: self.Record(0)).start()

    def StopRecording(self):
        self.recording = False

    def Record(self, delaySec):
        while self.recording:
            self.TakeAndMeasureImage()
            time.sleep(delaySec)

if __name__ == "__main__":
    Main()