import cv2
import os
import numpy
import PerformanceTimer as pt
from PIL import Image
from enum import Enum

class ImageProcessing():
    def __init__(self):
        self.thresholdValue = 90 #value between 0 and 255
        self.minObjectSize = 8000
        self.pixelsPerMilimeter = 157.5
        self.contourLineWidth = 2


    def ProcessImage(self, imageToProcess, numberOfMeasurements, borderOffset, pixelsPerMM, threshold, imageProcessingType, writeImages = False):
        pt.StartTimer()

        self.thresholdValue = threshold
        self.imageToProcess = imageToProcess
        self.imageProcessingType = imageProcessingType
        self.pixelsPerMilimeter = pixelsPerMM

        if self.imageProcessingType != 2:
            imageGrayscale = self.ConvertImageToGrayscale(self.PILToCV2(imageToProcess))
            threshold = self.GetThresholdImage(imageGrayscale)
            self.contourImage = self.DrawContours(self.GetContours(threshold), cv2.cvtColor(imageGrayscale, cv2.COLOR_GRAY2BGR))

        image, readings = self.GetDiameterOfImage(numberOfMeasurements, borderOffset)

        if writeImages:
            self.WriteImage(image, "contourImage")

        pt.StopTimer("Procssing image")

        return image, readings

    @staticmethod
    def PILToCV2(image):
        array = numpy.array(image)
        return cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
    
    @staticmethod
    def ConvertImageToGrayscale(image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def GetThresholdImage(self, img):
        _, threshold = cv2.threshold(img, self.thresholdValue, 255, cv2.THRESH_BINARY)
        return threshold

    @staticmethod
    def WriteImage(imageToWrite, imageName):
        if not cv2.imwrite("CapturedImages/"+ imageName +".png", imageToWrite):
            raise Exception("Could not write image")

    @staticmethod
    def ShowImage(imageToShow):
        cv2.imshow("image", imageToShow)

    @staticmethod
    def GetContours(thresholdImage):
        contours, _ = cv2.findContours(thresholdImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        return contours

    def DrawContours(self, contours, imageToDrawOn):
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.minObjectSize:
                cv2.drawContours(imageToDrawOn, contour, -1, (0, 0, 255), self.contourLineWidth)
        
        return imageToDrawOn

    def GetDiameterOfImage(self, numberOfMeasurements, sideBorder=0):
        imageWidth = self.imageToProcess.size[0]

        pixelsPerMeasurement = int((imageWidth - (sideBorder * 2)) / (numberOfMeasurements + 1))

        measurements = []

        for i in range(numberOfMeasurements):
            if self.imageProcessingType == 2:
                image, diameterReading = self.GetDiameterFromWidthPositionFilameter(self.imageToProcess, int((pixelsPerMeasurement * (i + 1)) + sideBorder))
            else:
                image, diameterReading = self.GetDiameterFromWidthPosition(self.contourImage, int((pixelsPerMeasurement * (i + 1)) + sideBorder))
                
            measurements.append(diameterReading)

        return image, measurements


    def GetDiameterFromWidthPosition(self, image, imagePositionWidth):
        imageHeight = image.shape[0]

        filamentTopPosition = 0
        filamentBottomPosition = 0

        for i in range(imageHeight):
            b, g, r = image[i, imagePositionWidth]

            if(r == 255 and g == 0 and b == 0):
                filamentTopPosition = i + self.contourLineWidth
                break

        for i in range(imageHeight - 1, -1, -1):
            b, g, r = image[i, imagePositionWidth]

            if(r == 255 and g == 0 and b == 0):
                filamentBottomPosition = i - self.contourLineWidth
                break

        image = cv2.line(image, (imagePositionWidth, filamentTopPosition), (imagePositionWidth, filamentBottomPosition), (0, 255, 0), 4)
        
        image = cv2.putText(image, str(filamentBottomPosition - filamentTopPosition) + 'px', (int(imagePositionWidth + 5), int(imageHeight / 2)), cv2.QT_FONT_NORMAL, 1, (255, 0, 0), 1, cv2.LINE_AA)
        image = cv2.putText(image, str(round((filamentBottomPosition - filamentTopPosition) / self.pixelsPerMilimeter, 3)) + 'mm', (int(imagePositionWidth + 5), int((imageHeight / 2) + 50)), cv2.QT_FONT_NORMAL, 1, (255, 0, 0), 1, cv2.LINE_AA)
        diameterInMM = round((filamentBottomPosition - filamentTopPosition) / self.pixelsPerMilimeter, 3)

        return image, diameterInMM

    @staticmethod
    def DrawPixel(x, y, color, image):
        image.putpixel((x, y), color)
        image.putpixel((x - 1, y), color)
        image.putpixel((x + 1, y), color)
        return image


    def GetDiameterFromWidthPositionFilameter(self, imageToProcess, xPosition):
        height = imageToProcess.size[1]
        image = imageToProcess.load()

        averageColor = None

        numberOfPixelsToGetAverageColorFrom = 100
        topPosition = 0
        bottomPosition = 0

        for i in range(int(height / 2), -1, -1):
            centerToDownwards = int(((height / 2) - i) + (height / 2) - 1)
            centerToUpwards = i


            if averageColor == None:
                averageColor = image[xPosition, centerToUpwards]
            elif i >= int(height / 2) - numberOfPixelsToGetAverageColorFrom:
                pixelColor = image[xPosition, centerToUpwards]
                averageColor = ((averageColor[0] + pixelColor[0]) / 2, (averageColor[1] + pixelColor[1]) / 2, (averageColor[2] + pixelColor[2]) / 2)
                imageToProcess = self.DrawPixel(xPosition, centerToDownwards, (0, 255, 0), imageToProcess)
                imageToProcess = self.DrawPixel(xPosition, centerToDownwards, (0, 255, 0), imageToProcess)

            else:
                rDifference = abs(image[xPosition, centerToUpwards][0] - averageColor[0])
                gDifference = abs(image[xPosition, centerToUpwards][1] - averageColor[1])
                bDifference = abs(image[xPosition, centerToUpwards][2] - averageColor[2])
                if rDifference >= self.thresholdValue or gDifference >= self.thresholdValue or bDifference >= self.thresholdValue:
                    imageToProcess = self.DrawPixel(xPosition, centerToUpwards, (0, 0, 255), imageToProcess)
                else:
                    topPosition = centerToUpwards
                    imageToProcess = self.DrawPixel(xPosition, centerToUpwards, (255, 0, 0), imageToProcess)

                rDifference = abs(image[xPosition, centerToDownwards][0] - averageColor[0])
                gDifference = abs(image[xPosition, centerToDownwards][1] - averageColor[1])
                bDifference = abs(image[xPosition, centerToDownwards][2] - averageColor[2])
                if rDifference >= self.thresholdValue or gDifference >= self.thresholdValue or bDifference >= self.thresholdValue:
                    imageToProcess = self.DrawPixel(xPosition, centerToDownwards, (0, 0, 255), imageToProcess)
                else:
                    bottomPosition = centerToDownwards
                    imageToProcess = self.DrawPixel(xPosition, centerToDownwards, (255, 0, 0), imageToProcess)

        diameterInMM = round((bottomPosition - topPosition) / self.pixelsPerMilimeter, 4)

        #imageToProcess.save("CapturedImages/FilameterImageProcessingTest.png")
            
        return imageToProcess, diameterInMM