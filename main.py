from tkinter import *
from enum import Enum
from os.path import exists

import customtkinter
import atexit
import CaptureImage as captureImage
import ImageProcessing as imageProcessing
import ImageManager as imageManager
import PerformanceTimer as pt
import FilamentCalculations as filamentCalculations
import JsonLoaderAndSaver as jsonLoaderAndSaver

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
    def __init__(self, ctkButton, text, setting, main):
        self.ctkButton = ctkButton
        self.text = text
        self.setting = setting
        self.main = main

    def Select(self):
        self.ctkButton.configure(fg_color="#7C98B3", hover_color="#7C98B3")

    def UnSelect(self):
        self.ctkButton.configure(fg_color="#292929", hover_color="#292929")

    def SetTextValue(self, value):
        self.ctkButton.configure(text=self.text + str(value))

    def UpdateTextValueFromSetting(self):
        self.ctkButton.configure(text=self.text + str(self.setting.GetValue()))


class FilamentViewFrame(customtkinter.CTkFrame):
    def __init__(self, parent, frameParent, *args, **kwargs):
        customtkinter.CTkFrame.__init__(self, frameParent, *args, **kwargs)
        self.parent = parent
        self.configure( width=620,
                        height=180,
                        corner_radius=4,
                        fg_color="#1E1E1E")
        self.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky=NW)
        self.imageLabel = customtkinter.CTkLabel(master=self, width=600, height=150, bg_color="#292929", corner_radius=0, text="")

        self.imageLabel.grid(row=0, column=0, padx=(10, 10), pady=(10, 10))

    def RefreshProcessedImage(self,processedImage):
        global contourImage
        contourImage = processedImage
        self.imageLabel.configure(image=contourImage)

class FilamentGraph(customtkinter.CTkFrame):
    def __init__(self, parent, frameParent, *args, **kwargs):
        customtkinter.CTkFrame.__init__(self, frameParent, *args, **kwargs)
        self.parent = parent
        self.configure( width=620,
                        height=64,
                        corner_radius=4,
                        fg_color="#1E1E1E")
        self.grid(row=1, column=0, padx=(0, 0), pady=(5, 0), sticky=NW)

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
        sideBorder = self.parent.settings.borderOffset.GetValue() * 0.3
        pixelsPerMeasurement = int((canvasWidth - (sideBorder * 2)) / (numberOfMeasurements + 1))

        position = int((pixelsPerMeasurement * (measurementIndex + 1)) + sideBorder)
        return position

    def ClearCanvas(self):
        for i in range(len(self.drawnLines)):
            self.graphCanvas.delete(self.drawnLines[i])


class FilamentInfo(customtkinter.CTkFrame):
    def __init__(self, parent, frameParent, *args, **kwargs):
        customtkinter.CTkFrame.__init__(self, frameParent, *args, **kwargs)
        self.parent = parent
        self.configure( width=165,
                        height=120,
                        corner_radius=4,
                        fg_color="#1E1E1E")
        self.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky=NE)
        self.grid_propagate(0)

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
    def __init__(self, parent, frameParent, *args, **kwargs):
        customtkinter.CTkFrame.__init__(self, frameParent, *args, **kwargs)
        self.parent = parent
        self.configure( width=150,
                        height=180,
                        corner_radius=4,
                        fg_color="#1E1E1E")

        self.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky=NW)
        self.grid_propagate(0)

        self.headerLabel = customtkinter.CTkLabel(master=self, text="Single Actions", text_color="#ffffff", text_font='Helvetica 11 bold')
        self.headerLabel.grid(row=0, column=0, padx=(2, 2), pady=(2, 0))

        self.captureAndProcessButton = customtkinter.CTkButton(master=self, text="Process \n & \n capture", fg_color=parent.buttonColor, hover_color=parent.buttonHoverColor, text_font=("Arial Baltic", 11), width=80, height=65,command= lambda: ButtonHelper.DisableButtonWhenRelatedTaskIsRunning(threading.Thread(target=parent.TakeAndMeasureImage), self.captureAndProcessButton))
        self.captureAndProcessButton.grid(row=1, column=0, padx=(10, 10), pady=(2, 5))

        self.previewButton = customtkinter.CTkButton(master=self, text="Preview",  fg_color=parent.buttonColor, hover_color=parent.buttonHoverColor, text_font=("", 11), width=80, height=55, command=captureImage.Preview)
        self.previewButton.grid(row=2, column=0, padx=(10, 10), pady=(5, 10))

class ControlPad(customtkinter.CTkFrame):
    def __init__(self, parent, frameParent, *args, **kwargs):
        customtkinter.CTkFrame.__init__(self, frameParent, *args, **kwargs)
        self.parent = parent
        self.configure( width=165,
                        height=175,
                        corner_radius=4,
                        fg_color="#1E1E1E")

        self.grid(row=2, column=0, padx=(0, 0), pady=(5, 0), sticky=NE)

        self.grid_propagate(0)

        self.selectedButton = None
        self.addValue = 0

        self.headerLabel = customtkinter.CTkLabel(master=self, text="Control", text_color="#ffffff", text_font='Helvetica 11 bold')
        self.headerLabel.grid(row=0, column=0, padx=(2, 2), pady=(2, 0))

        self.addButton = customtkinter.CTkButton(master=self, text="+", fg_color=parent.buttonColor, hover_color=parent.buttonHoverColor, text_font=("", 16), width=50, height=50, command= lambda: self.parent.settingsFrame.AddSelectedValue(self.addValue))
        self.addButton.grid(row=1, column=0, padx=(10, 10), pady=(2, 5), sticky=W)

        self.subtractButton = customtkinter.CTkButton(master=self, text="-",  fg_color=parent.buttonColor, hover_color=parent.buttonHoverColor, text_font=("", 16), width=50, height=50, command= lambda: self.parent.settingsFrame.AddSelectedValue(- self.addValue))
        self.subtractButton.grid(row=1, column=0, padx=(10, 10), pady=(2, 5), sticky=E)

        self.addAmountButton02 = customtkinter.CTkButton(master=self, text="", fg_color="#292929", hover_color="#292929", text_font=("", 11), text_color="#ffffff", width=40, height=38)
        self.addAmountButton02.grid(row=2, column=0, padx=(5, 0), pady=(2, 5), sticky=W)
        self.addAmountButton02Setting = ValueToggleButton(self.addAmountButton02, 0.2)
        self.addAmountButton02.configure(command=lambda: self.Select(self.addAmountButton02Setting))
        self.addAmountButton02Setting.DisplayValue()

        self.addAmountButton1 = customtkinter.CTkButton(master=self, text="", fg_color="#292929", hover_color="#292929", text_font=("", 11), text_color="#ffffff", width=40, height=38)
        self.addAmountButton1.grid(row=2, column=0, padx=(53, 0), pady=(2, 5), sticky=W)
        self.addAmountButton1Setting = ValueToggleButton(self.addAmountButton1, 1)
        self.addAmountButton1.configure(command=lambda: self.Select(self.addAmountButton1Setting))
        self.addAmountButton1Setting.DisplayValue()

        self.addAmountButton10 = customtkinter.CTkButton(master=self, text="", fg_color="#292929", hover_color="#292929", text_font=("", 11), text_color="#ffffff", width=40, height=38)
        self.addAmountButton10.grid(row=2, column=0, padx=(100, 0), pady=(2, 5), sticky=W)
        self.addAmountButton10Setting = ValueToggleButton(self.addAmountButton10, 10)
        self.addAmountButton10.configure(command=lambda: self.Select(self.addAmountButton10Setting))
        self.addAmountButton10Setting.DisplayValue()

        self.addAmountButton05 = customtkinter.CTkButton(master=self, text="", fg_color="#292929", hover_color="#292929", text_font=("", 11), text_color="#ffffff", width=40, height=38)
        self.addAmountButton05.grid(row=3, column=0, padx=(5, 0), pady=(2, 5), sticky=W)
        self.addAmountButton05Setting = ValueToggleButton(self.addAmountButton05, 0.5)
        self.addAmountButton05.configure(command=lambda: self.Select(self.addAmountButton05Setting))
        self.addAmountButton05Setting.DisplayValue()

        self.addAmountButton5 = customtkinter.CTkButton(master=self, text="", fg_color="#292929", hover_color="#292929", text_font=("", 11), text_color="#ffffff", width=40, height=38)
        self.addAmountButton5.grid(row=3, column=0, padx=(53, 0), pady=(2, 5), sticky=W)
        self.addAmountButton5Setting = ValueToggleButton(self.addAmountButton5, 5)
        self.addAmountButton5.configure(command=lambda: self.Select(self.addAmountButton5Setting))
        self.addAmountButton5Setting.DisplayValue()

        self.addAmountButton100 = customtkinter.CTkButton(master=self, text="", fg_color="#292929", hover_color="#292929", text_font=("", 11), text_color="#ffffff", width=40, height=38)
        self.addAmountButton100.grid(row=3, column=0, padx=(100, 0), pady=(2, 5), sticky=W)
        self.addAmountButton100Setting = ValueToggleButton(self.addAmountButton100, 100)
        self.addAmountButton100.configure(command=lambda: self.Select(self.addAmountButton100Setting))
        self.addAmountButton100Setting.DisplayValue()

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
    INT = 1
    FLOAT = 2
    BOOL = 3
    LIST = 4

class ImageProcessingType(Enum):
    OPENCV = 1
    FILAMETER = 2

class Setting():
    def __init__(self, value, settingType):
        self.value = value
        self.settingType = settingType

    def GetValue(self):
        if self.settingType == SettingType.INT:
            return int(self.value)
        elif self.settingType == SettingType.FLOAT:
            return round(float(self.value), 3)
        elif self.settingType == SettingType.BOOL:
            if self.value != 0:
                return True
            return False 
        elif self.settingType == SettingType.LIST:
            return self.value[0]
        return None

    def Set(self, value):
        self.value = value

    def Add(self, value):
        if self.settingType == SettingType.INT:
            self.value += int(value)
            return
        elif self.settingType == SettingType.FLOAT:
            self.value += float(value)
            return
        elif self.settingType == SettingType.BOOL:
            if self.value == 0:
                self.value == 1
                return
            self.value == 0
            return
        elif self.settingType == SettingType.LIST:
            self.value.insert(0, self.value.pop())
            return
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class Settings():
    def __init__(self):
        self.numberOfMeasurements = Setting(4, SettingType.INT)
        self.borderOffset = Setting(200, SettingType.INT)
        self.pixelsPerMM = Setting(371, SettingType.FLOAT)
        self.threshold = Setting(120, SettingType.INT)
        self.imageProcessingType = Setting([ImageProcessingType.FILAMETER, ImageProcessingType.OPENCV], SettingType.LIST)
    
    @property
    def __json__(self):
        return {
            "numberOfMeasurements": f"{self.numberOfMeasurements.value}",
            "borderOffset": f"{self.borderOffset.value}",
            "pixelsPerMM": f"{self.pixelsPerMM.value}",
            "threshold": f"{self.threshold.value}",
            "imageProcessingType": f"{[self.imageProcessingType.value[0].name, self.imageProcessingType.value[1].name]}",
        }

    def LoadFromJSON(self, json):
        self.numberOfMeasurements.value = int(json["numberOfMeasurements"])
        self.borderOffset.value = int(json["borderOffset"])
        self.pixelsPerMM.value = float(json["pixelsPerMM"])
        self.threshold.value = int(json["threshold"])
        res = json["imageProcessingType"].strip("[]").replace("'", '').split(', ')
        self.imageProcessingType.value = [ImageProcessingType[res[0]], ImageProcessingType[res[1]]]

class SettingsFrame(customtkinter.CTkFrame):
    def __init__(self, parent, frameParent, *args, **kwargs):
        customtkinter.CTkFrame.__init__(self, frameParent, *args, **kwargs)
        self.parent = parent
        self.configure( width=465,
                        height=180,
                        corner_radius=4,
                        fg_color="#1E1E1E")
        self.grid_propagate(0)
        self.grid(row=0, column=1, padx=(5, 0), pady=(0, 0), sticky=NW)

        self.selectedButton = None

        self.settings0 = customtkinter.CTkFrame(master=self,
                               width=465,
                               height=140,
                               corner_radius=0,
                               fg_color="#1E1E1E")
        self.settings0.grid(row=1, column=0, padx=(0, 0), pady=(0, 0), sticky=NW)
        self.settings0.grid_propagate(0)

        self.settings1 = customtkinter.CTkFrame(master=self,
                               width=465,
                               height=140,
                               corner_radius=0,
                               fg_color="#1E1E1E")
        self.settings1.grid_propagate(0)

        self.headerLabel = customtkinter.CTkLabel(master=self, text="Settings", text_color="#ffffff", text_font='Helvetica 11 bold')
        self.headerLabel.grid(row=0, column=0, padx=(2, 2), pady=(2, 0), sticky=W)

        self.settings0Button = customtkinter.CTkButton(master=self, text="0", fg_color="#292929", hover_color="#292929", text_font=("", 11), text_color="#ffffff", width=35, height=30, command= lambda: self.ShowFrame(self.settings0))
        self.settings0Button.grid(row=0, column=0, padx=(110, 0), pady=(2, 0), sticky=W)

        self.settings1Button = customtkinter.CTkButton(master=self, text="1", fg_color="#292929", hover_color="#292929", text_font=("", 11), text_color="#ffffff", width=35, height=30, command= lambda: self.ShowFrame(self.settings1))
        self.settings1Button.grid(row=0, column=0, padx=(150, 0), pady=(2, 0), sticky=W)


        self.numberOfMeasurementsButton = customtkinter.CTkButton(master=self.settings0, fg_color="#292929", hover_color="#292929", text_font=("", 11), text_color="#ffffff", width=150, height=30)
        self.numberOfMeasurementsButton.grid(row=1, column=0, padx=(10, 2), pady=(2, 5), sticky=W)
        self.numberOfMeasurementsButton.grid_propagate(0)
        self.numberOfMeasurementsSetting = SettingsButton(self.numberOfMeasurementsButton, "No of M. ", self.parent.settings.numberOfMeasurements, self.parent)
        self.numberOfMeasurementsButton.configure(command=lambda: self.Select(self.numberOfMeasurementsSetting))
        self.numberOfMeasurementsSetting.UpdateTextValueFromSetting()

        self.measureBorderOffsetButton = customtkinter.CTkButton(master=self.settings0, text="M. border offset", fg_color="#292929", hover_color="#292929", text_font=("", 11), text_color="#ffffff", width=150, height=40)
        self.measureBorderOffsetButton.grid(row=2, column=0, padx=(10, 2), pady=(2, 5), sticky=W)
        self.measureBorderOffsetButton.grid_propagate(0)
        self.measureBorderOffsetButtonSetting = SettingsButton(self.measureBorderOffsetButton, "M. border offset ", self.parent.settings.borderOffset, self.parent)
        self.measureBorderOffsetButton.configure(command=lambda: self.Select(self.measureBorderOffsetButtonSetting))
        self.measureBorderOffsetButtonSetting.UpdateTextValueFromSetting()

        self.pixelsPerMMButton = customtkinter.CTkButton(master=self.settings0, text="pixels per mm", fg_color="#292929", hover_color="#292929", text_font=("", 11), text_color="#ffffff", width=150, height=40)
        self.pixelsPerMMButton.grid(row=3, column=0, padx=(10, 2), pady=(2, 5), sticky=W)
        self.pixelsPerMMButton.grid_propagate(0)
        self.pixelsPerMMButtonSetting = SettingsButton(self.pixelsPerMMButton, "pixels per mm ", self.parent.settings.pixelsPerMM, self.parent)
        self.pixelsPerMMButton.configure(command=lambda: self.Select(self.pixelsPerMMButtonSetting))
        self.pixelsPerMMButtonSetting.UpdateTextValueFromSetting()

        self.thresholdButton = customtkinter.CTkButton(master=self.settings0, text="threshold", fg_color="#292929", hover_color="#292929", text_font=("", 11), text_color="#ffffff", width=150, height=40)
        self.thresholdButton.grid(row=1, column=1, padx=(2, 2), pady=(2, 5), sticky=W)
        self.thresholdButton.grid_propagate(0)
        self.thresholdButtonSetting = SettingsButton(self.thresholdButton, "threshold ", self.parent.settings.threshold, self.parent)
        self.thresholdButton.configure(command=lambda: self.Select(self.thresholdButtonSetting))
        self.thresholdButtonSetting.UpdateTextValueFromSetting()

        self.imageProcessingTypeButton = customtkinter.CTkButton(master=self.settings1, text="threshold", fg_color="#292929", hover_color="#292929", text_font=("", 11), text_color="#ffffff", width=250, height=40)
        self.imageProcessingTypeButton.grid(row=1, column=1, padx=(2, 2), pady=(2, 5), sticky=W)
        self.imageProcessingTypeButton.grid_propagate(0)
        self.imageProcessingTypeButtonSetting = SettingsButton(self.imageProcessingTypeButton, "threshold ", self.parent.settings.imageProcessingType, self.parent)
        self.imageProcessingTypeButton.configure(command=lambda: self.Select(self.imageProcessingTypeButtonSetting))
        self.imageProcessingTypeButtonSetting.UpdateTextValueFromSetting()


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
        
        self.selectedButton.setting.Add(value)
        self.selectedButton.UpdateTextValueFromSetting()

    def ShowFrame(self, frameToShow):
        self.settings0.grid_forget()
        self.settings1.grid_forget()

        frameToShow.grid(row=1, column=0, padx=(0, 0), pady=(0, 0), sticky=NW)



class RecordPad(customtkinter.CTkFrame):
    def __init__(self, parent, frameParent, *args, **kwargs):
        customtkinter.CTkFrame.__init__(self, frameParent, *args, **kwargs)
        self.parent = parent
        self.configure( width=165,
                        height=120,
                        corner_radius=4,
                        fg_color="#1E1E1E")

        self.grid(row=1, column=0, padx=(0, 0), pady=(5, 0), sticky=NE)
        self.grid_propagate(0)


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
        self.tolerance = max(toleranceValues)
        self.averageDiameter = averageDiameter / len(measurementInfoList)

class FilamentRecording():
    def __init__(self):
        self.maxDiameter = 0
        self.minDiameter = 99
        self.tolerance = None
        self.measurementInfoGroupList = []

    def AddMeasurementInfoGroup(self, measurementInfoGroup):
        self.measurementInfoGroupList.append(measurementInfoGroup)

        if self.maxDiameter < measurementInfoGroup.maxDiameter:
            self.maxDiameter = measurementInfoGroup.maxDiameter
        if self.minDiameter > measurementInfoGroup.minDiameter:
            self.minDiameter = measurementInfoGroup.minDiameter

    def FinishRecording(self):
        self.tolerance = (self.maxDiameter - self.minDiameter) / 2

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
        

class Main(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        customtkinter.CTk.__init__(self, *args, **kwargs)
        self.geometry("800x480")
        self.configure(bg='#121212')
        self.title("Filameter")

        self.buttonColor = "#F5BEE0"
        self.buttonHoverColor = "#F9DCEE"

        self.recordingThread = None
        self.recording = False

        self.lastMeasurementInfo = None

        self.filamentRecording = None

        #settings
        self.settings = Settings()

        if exists("settings.json"):
            self.settings.LoadFromJSON(jsonLoaderAndSaver.GetJSON("settings"))

        #frames to organize the layout
        layoutFramesBackgroundColor = "#121212"

        topLeftFrame = customtkinter.CTkFrame(master=self,
                               width=620,
                               height=250,
                               corner_radius=0,
                               fg_color=layoutFramesBackgroundColor)
        topLeftFrame.grid(row=0, column=0, padx=(5, 5), pady=(5, 0), sticky=NW)
        topLeftFrame.grid_propagate(0)

        bottomLeftFrame = customtkinter.CTkFrame(master=self,
                               width=620,
                               height=200,
                               corner_radius=0,
                               fg_color=layoutFramesBackgroundColor)
        bottomLeftFrame.grid(row=1, column=0, padx=(5, 5), pady=(5, 0), sticky=NW)
        bottomLeftFrame.grid_propagate(0)

        rightFrame = customtkinter.CTkFrame(master=self,
                               width=165,
                               height=470,
                               corner_radius=0,
                               fg_color=layoutFramesBackgroundColor)
        rightFrame.grid(row=0, column=1, padx=(0, 5), pady=(5, 0), sticky=NE, rowspan=2)
        rightFrame.grid_propagate(0)

        #frames
        self.filamentViewFrame = FilamentViewFrame(self, topLeftFrame)
        self.filamentGraph = FilamentGraph(self, topLeftFrame)
        self.buttonFrame = ButtonFrame(self, bottomLeftFrame)
        self.settingsFrame = SettingsFrame(self, bottomLeftFrame)
        self.controlPad = ControlPad(self, rightFrame)
        self.recordPad = RecordPad(self, rightFrame)
        self.filamentInfo= FilamentInfo(self, rightFrame)

        self.imageProcessing = imageProcessing.ImageProcessing()

        self.mainloop();

    def TakeAndMeasureImage(self):
        capturedimage = captureImage.CaptureImage()
        processedImage, measurements = self.imageProcessing.ProcessImage(capturedimage, self.settings.numberOfMeasurements.GetValue(), self.settings.borderOffset.GetValue(), self.settings.pixelsPerMM.GetValue(), self.settings.threshold.GetValue(), self.settings.imageProcessingType.GetValue())
        
        self.lastMeasurementInfo = MeasurementInfo(measurements, filamentCalculations.GetAverageFromReadings(measurements), filamentCalculations.GetToleranceFromReadings(measurements))

        pt.StartTimer()

        if self.settings.imageProcessingType.GetValue().value == ImageProcessingType.FILAMETER.value:
            self.filamentViewFrame.RefreshProcessedImage(imageManager.PILToTKAndResize(processedImage, 600, 150))
        else:
            self.filamentViewFrame.RefreshProcessedImage(imageManager.CV2ToTKAndResize(processedImage, 600, 150))

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
        self.filamentRecording = FilamentRecording()
        self.recordingThread = threading.Thread(target= lambda: self.Record(0)).start()

    def StopRecording(self):
        self.recording = False
        self.filamentRecording.FinishRecording()
        jsonLoaderAndSaver.SaveFilamentRecordingToJSON(self.filamentRecording)

    def Record(self, delaySec):
        measurementInfoList = []

        while self.recording:
            self.TakeAndMeasureImage()
            measurementInfoList.append(self.lastMeasurementInfo)
            if 5 <= len(measurementInfoList):
                self.filamentRecording.AddMeasurementInfoGroup(MeasurementInfoGroup(measurementInfoList))
                measurementInfoList = []

            time.sleep(delaySec)

    def exit_handler(self):
        jsonLoaderAndSaver.SaveObjectToJSON(self.settings, "settings")
        


if __name__ == "__main__":
    main = Main() 
    atexit.register(main.exit_handler)
