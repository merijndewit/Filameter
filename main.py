from ast import arguments
from cgitb import text
from contextlib import nullcontext
from tkinter import *
from enum import Enum

import customtkinter
import CaptureImage as captureImage
import ImageProcessing as imageProcessing
import ImageManager as imageManager
import PerformanceTimer as pt
import FilamentCalculations as filamentCalculations
import RecordingSaver as recordingSaver

import threading
import time
import json

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

class FilamentGraph(customtkinter.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        customtkinter.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.configure( width=620,
                        height=64,
                        corner_radius=4,
                        fg_color="#1E1E1E")
        self.grid(row=1, column=0, padx=(10, 10), pady=(5, 5), sticky=W)

        self.targetDiameter = 1.750

        self.graphCanvas = Canvas(self, bg='#1E1E1E', width=610, height=64, highlightthickness=0)
        self.graphCanvas.grid(row=0, column=0, padx=(5, 5), pady=(5, 5))

        self.graphCanvas.create_line(0, 32, 550, 32, fill="#ffffff", width=1)
        self.graphCanvas.create_text(608,32,fill="#ffffff",font="Helvetica 8 bold", text=str(self.targetDiameter) + "mm", anchor=E)

        self.maxText = self.graphCanvas.create_text(608,8,fill="#ffffff",font="Helvetica 8 bold", text=str(self.targetDiameter) + "mm", anchor=E)
        self.minText = self.graphCanvas.create_text(608,56,fill="#ffffff",font="Helvetica 8 bold", text=str(self.targetDiameter) + "mm", anchor=E)
        self.maxLine = self.graphCanvas.create_line(0, 56, 550, 56, fill="#aaaaaa", width=1)
        self.minLine = self.graphCanvas.create_line(0, 8, 550, 8, fill="#aaaaaa", width=1)


        self.drawnLines = []

    def DrawGraphFromReadings(self, readings):
        self.ClearCanvas()
        numberOfMeasurements = len(readings.measurements)
        maxNumber = max(abs(readings.minDiameter - self.targetDiameter), readings.maxDiameter - self.targetDiameter)

        displacementMultiplier = 24 / maxNumber

        self.graphCanvas.itemconfig(self.maxText, text="+" + str(round(maxNumber, 3)) + "mm")
        self.graphCanvas.itemconfig(self.minText, text="-" + str(round(maxNumber, 3)) + "mm")

        for i in range(numberOfMeasurements - 1):
            yPos0 = ((self.targetDiameter - readings.measurements[i]) * displacementMultiplier) + 32
            yPos1 = ((self.targetDiameter - readings.measurements[i + 1]) * displacementMultiplier) + 32
            line = self.graphCanvas.create_line(self.GetXdrawingPosition(numberOfMeasurements, i, 610), yPos0, self.GetXdrawingPosition(numberOfMeasurements, i + 1, 610), yPos1, fill="#7C98B3", width=4)
            self.drawnLines.append(line)

    def DrawGraphFromRecording(self, recording):
        self.ClearCanvas()
        numberOfMeasurements = len(recording.measurementInfoGroupList)
        if numberOfMeasurements <= 1:
            return
        maxNumber = max(abs(recording.minDiameter - self.targetDiameter), recording.maxDiameter - self.targetDiameter)

        displacementMultiplier = 24 / maxNumber

        self.graphCanvas.itemconfig(self.maxText, text="+" + str(round(maxNumber, 3)) + "mm")
        self.graphCanvas.itemconfig(self.minText, text="-" + str(round(maxNumber, 3)) + "mm")


        for i in range(numberOfMeasurements - 1):
            yPos0 = ((self.targetDiameter - recording.measurementInfoGroupList[i].averageDiameter) * displacementMultiplier) + 32
            yPos1 = ((self.targetDiameter - recording.measurementInfoGroupList[i + 1].averageDiameter) * displacementMultiplier) + 32
            line = self.graphCanvas.create_line(self.GetXdrawingPosition(numberOfMeasurements, i, 610), yPos0, self.GetXdrawingPosition(numberOfMeasurements, i + 1, 610), yPos1, fill="#7C98B3", width=4)
            self.drawnLines.append(line)

    def GetXdrawingPosition(self, numberOfMeasurements, measurementIndex, canvasWidth):
        sideBorder = self.parent.settings.GetSetting(SettingType.BORDEROFFSET).GetValue() * 0.3
        pixelsPerMeasurement = int((canvasWidth - (sideBorder * 2)) / (numberOfMeasurements + 1))

        position = int((pixelsPerMeasurement * (measurementIndex + 1)) + sideBorder)
        return position

    def ClearCanvas(self):
        for i in range(len(self.drawnLines)):
            self.graphCanvas.delete(self.drawnLines[i])


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

        self.toleranceText = customtkinter.CTkLabel(master=self, text="Tolerance: ", text_color="#ffffff")
        self.toleranceText.grid(row=2, column=0, padx=(2, 2), pady=(2, 0))

    def SetAverageTextValue(self, value):
        self.averageText.configure(text="Avg dia: " + str(round(value, 3)) + "mm")

    def SetToleranceTextValue(self, value):
        self.toleranceText.configure(text="Tolerance: +/-" + str(round(value, 3)) + "mm")

class ValueToggleButton():
    def __init__(self, ctkButton, value):
        self.ctkButton = ctkButton
        self.value = value

    def Select(self):
        self.ctkButton.configure(fg_color="#7C98B3", hover_color="#7C98B3")

    def UnSelect(self):
        self.ctkButton.configure(fg_color="#292929", hover_color="#292929")

    def DisplayValue(self):
        self.ctkButton.configure(text=str(self.value))

class ButtonFrame(customtkinter.CTkFrame):  
    def __init__(self, parent, *args, **kwargs):
        customtkinter.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.configure( width=150,
                        height=200,
                        corner_radius=4,
                        fg_color="#1E1E1E")

        self.grid(row=2, column=0, padx=(10, 0), pady=(5, 0), sticky=W)

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

        self.grid(row=2, column=0, padx=(600, 5), pady=(5, 0), sticky=NE)

        self.selectedButton = None
        self.addValue = 0

        self.headerLabel = customtkinter.CTkLabel(master=self, text="Control", text_color="#ffffff", text_font='Helvetica 11 bold')
        self.headerLabel.grid(row=0, column=0, padx=(2, 2), pady=(2, 0))

        self.addButton = customtkinter.CTkButton(master=self, text="+", fg_color=parent.buttonColor, hover_color=parent.buttonHoverColor, text_font=("", 16), width=50, height=50, command= lambda: self.parent.settingsFrame.AddSelectedValue(self.addValue))
        self.addButton.grid(row=1, column=0, padx=(10, 10), pady=(2, 5), sticky=W)

        self.subtractButton = customtkinter.CTkButton(master=self, text="-",  fg_color=parent.buttonColor, hover_color=parent.buttonHoverColor, text_font=("", 16), width=50, height=50, command= lambda: self.parent.settingsFrame.AddSelectedValue(- self.addValue))
        self.subtractButton.grid(row=1, column=0, padx=(10, 10), pady=(5, 10), sticky=E)

        self.addAmountButton02 = customtkinter.CTkButton(master=self, text="", fg_color="#292929", hover_color="#292929", text_font=("", 11), text_color="#ffffff", width=35, height=35)
        self.addAmountButton02.grid(row=2, column=0, padx=(5, 0), pady=(2, 5), sticky=W)
        self.addAmountButton02Setting = ValueToggleButton(self.addAmountButton02, 0.2)
        self.addAmountButton02.configure(command=lambda: self.Select(self.addAmountButton02Setting))
        self.addAmountButton02Setting.DisplayValue()

        self.addAmountButton1 = customtkinter.CTkButton(master=self, text="", fg_color="#292929", hover_color="#292929", text_font=("", 11), text_color="#ffffff", width=35, height=35)
        self.addAmountButton1.grid(row=2, column=0, padx=(50, 0), pady=(2, 5), sticky=W)
        self.addAmountButton1Setting = ValueToggleButton(self.addAmountButton1, 1)
        self.addAmountButton1.configure(command=lambda: self.Select(self.addAmountButton1Setting))
        self.addAmountButton1Setting.DisplayValue()

        self.addAmountButton5 = customtkinter.CTkButton(master=self, text="", fg_color="#292929", hover_color="#292929", text_font=("", 11), text_color="#ffffff", width=35, height=35)
        self.addAmountButton5.grid(row=2, column=0, padx=(90, 0), pady=(2, 5), sticky=W)
        self.addAmountButton5Setting = ValueToggleButton(self.addAmountButton5, 5)
        self.addAmountButton5.configure(command=lambda: self.Select(self.addAmountButton5Setting))
        self.addAmountButton5Setting.DisplayValue()

        self.Select(self.addAmountButton1Setting)


    def Select(self, selectedButton):
        if selectedButton == self.selectedButton:
            selectedButton.UnSelect()
            self.selectedButton = None
            self.addValue = 0
            return
        if self.selectedButton is not None:
            self.selectedButton.UnSelect()
        self.selectedButton = selectedButton
        selectedButton.Select()
        self.addValue = selectedButton.value

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



class SettingsFrame(customtkinter.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        customtkinter.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.configure( width=150,
                        height=200,
                        corner_radius=4,
                        fg_color="#1E1E1E")

        self.grid(row=2, column=0, padx=(200, 30), pady=(5, 0), sticky=NW)

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

        self.grid(row=2, column=0, padx=(320, 30), pady=(5, 0), sticky=N)

        self.headerLabel = customtkinter.CTkLabel(master=self, text="Record", text_color="#ffffff", text_font='Helvetica 11 bold')
        self.headerLabel.grid(row=0, column=0, padx=(2, 2), pady=(2, 0))

        self.addButton = customtkinter.CTkButton(master=self, text="Start", fg_color=parent.buttonColor, hover_color=parent.buttonHoverColor, text_font=("", 11), width=55, height=35, command= lambda: self.parent.StartRecording())
        self.addButton.grid(row=1, column=0, padx=(5, 2), pady=(2, 5), sticky=W)

        self.subtractButton = customtkinter.CTkButton(master=self, text="Stop",  fg_color=parent.buttonColor, hover_color=parent.buttonHoverColor, text_font=("", 11), width=55, height=35, command= lambda: self.parent.StopRecording())
        self.subtractButton.grid(row=1, column=0, padx=(2, 5), pady=(5, 10), sticky=E)

class MeasurementInfo():
    def __init__(self, measurements, averageDiameter, tolerance):
        self.measurements = measurements
        self.averageDiameter = averageDiameter
        self.minDiameter = min(measurements)
        self.maxDiameter = max(measurements)
        self.tolerance = tolerance

class MeasurementInfoGroup():
    def __init__(self, measurementInfoList):
        self.tolerance = None

        averageDiameter = 0


        for i in range(len(measurementInfoList)):
            minValues = []
            maxValues = []
            toleranceValues = []

            minValues.append(measurementInfoList[i].minDiameter)
            maxValues.append(measurementInfoList[i].maxDiameter)
            toleranceValues.append(measurementInfoList[i].tolerance)

            averageDiameter += measurementInfoList[i].averageDiameter

        self.minDiameter = min(minValues)
        self.maxDiameter = max(maxValues)
        self.averageDiameter = averageDiameter / len(measurementInfoList)



class FilamentRecording():
    def __init__(self, measurementInfoPerGroup):
        self.measurementInfoList = []
        self.measurementInfoGroupList = []
        self.maxDiameter = 0
        self.minDiameter = 99
        self.tolerance = None
        self.measurementInfoPerGroup = measurementInfoPerGroup
        
    def AddMeasurementInfo(self, measurementInfo):
        self.measurementInfoList.append(measurementInfo)

        if self.maxDiameter < measurementInfo.maxDiameter:
            self.maxDiameter = measurementInfo.maxDiameter
        if self.minDiameter > measurementInfo.minDiameter:
            self.minDiameter = measurementInfo.minDiameter

        if self.measurementInfoPerGroup <= len(self.measurementInfoList):
            print("add info group")
            self.measurementInfoGroupList.append(MeasurementInfoGroup(self.measurementInfoList))
            self.measurementInfoList = []
        

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
        

class Main(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        customtkinter.CTk.__init__(self, *args, **kwargs)
        self.geometry("800x480")
        self.configure(bg='#121212')

        self.buttonColor = "#F5BEE0"
        self.buttonHoverColor = "#F9DCEE"

        self.recordingThread = None
        self.recording = False

        self.lastMeasurementInfo = None

        self.filamentRecording = None

        #settings
        self.settings = Settings()

        #frames
        self.filamentViewFrame = FilamentViewFrame(self)
        self.filamentGraph = FilamentGraph(self)
        self.buttonFrame = ButtonFrame(self)
        self.settingsFrame = SettingsFrame(self)
        self.controlPad = ControlPad(self)
        self.recordPad = RecordPad(self)
        self.filamentInfo= FilamentInfo(self)

        self.imageProcessing = imageProcessing.ImageProcessing()

        self.mainloop();

    def TakeAndMeasureImage(self):
        capturedimage = captureImage.CaptureImage()
        processedImage, measurements = self.imageProcessing.ProcessImage(capturedimage, self.settings.GetSetting(SettingType.NUMBEROFMEASUREMENTS).GetValueInt(), self.settings.GetSetting(SettingType.BORDEROFFSET).GetValueInt(), self.settings.GetSetting(SettingType.PIXELSPERMM).GetValueFloat())
        
        self.lastMeasurementInfo = MeasurementInfo(measurements, filamentCalculations.GetAverageFromReadings(measurements), filamentCalculations.GetToleranceFromReadings(measurements))

        pt.StartTimer()

        self.filamentViewFrame.RefreshProcessedImage(imageManager.CV2ToTKAndResize(processedImage, 0.30))

        pt.StopTimer("Refreshing images")

        if self.recording:
            self.DisplayRecordingInfo()
            return
        self.DisplaySingleReadingInfo()

    def DisplaySingleReadingInfo(self):
        self.filamentGraph.DrawGraphFromReadings(self.lastMeasurementInfo)
        self.filamentInfo.SetAverageTextValue(self.lastMeasurementInfo.averageDiameter)
        self.filamentInfo.SetToleranceTextValue(self.lastMeasurementInfo.tolerance)

    def DisplayRecordingInfo(self):
        self.filamentGraph.DrawGraphFromRecording(self.filamentRecording)
        self.filamentInfo.SetAverageTextValue(self.lastMeasurementInfo.averageDiameter)
        self.filamentInfo.SetToleranceTextValue(self.lastMeasurementInfo.tolerance)

    def StartRecording(self):
        self.recording = True
        self.filamentRecording = FilamentRecording(5)
        self.recordingThread = threading.Thread(target= lambda: self.Record(0)).start()

    def StopRecording(self):
        self.recording = False
        recordingSaver.SaveFilamentRecordingToJSON(self.filamentRecording)

    def Record(self, delaySec):
        while self.recording:
            self.TakeAndMeasureImage()
            self.filamentRecording.AddMeasurementInfo(self.lastMeasurementInfo)
            time.sleep(delaySec)

if __name__ == "__main__":
    Main() 