import cv2
import os

import PerformanceTimer as pt

thresholdValue = 110 #value between 0 and 255
minObjectSize = 8000
pixelsPerMilimeter = 157.5

contourLineWidth = 2

def ProcessImage():
    pt.StartTimer()
    img = GetGrayscaleCapturedImage()
    threshold = GetThresholdImage(img)
    contourImage = DrawContours(GetContours(threshold), cv2.cvtColor(GetGrayscaleCapturedImage(), cv2.COLOR_GRAY2BGR))

    contourImage = GetDiameterOfImage(contourImage, 11)

    WriteImage(contourImage, "contourImage")
    pt.StopTimer("Procssing image")
    #WriteImage(threshold, "processedImage")

def GetGrayscaleCapturedImage():
    return cv2.imread(os.path.dirname(os.path.realpath(__file__)) + "/CapturedImages/capture.png", cv2.IMREAD_GRAYSCALE)

def GetCapturedImage():
    return cv2.imread(os.path.dirname(os.path.realpath(__file__)) + "/CapturedImages/capture.png", cv2.IMREAD_ANYCOLOR)

def GetThresholdImage(img):
    _, threshold = cv2.threshold(img, thresholdValue, 255, cv2.THRESH_BINARY)
    return threshold

def WriteImage(imageToWrite, imageName):
    if not cv2.imwrite("CapturedImages/"+ imageName +".png", imageToWrite):
        raise Exception("Could not write image")

def ShowImage(imageToShow):
    cv2.imshow("image", imageToShow)

def GetContours(thresholdImage):
    contours, _ = cv2.findContours(thresholdImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    return contours

def DrawContours(contours, imageToDrawOn):
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > minObjectSize:
            cv2.drawContours(imageToDrawOn, contour, -1, (0, 0, 255), contourLineWidth)
    
    return imageToDrawOn

def GetDiameterOfImage(image, numberOfMeasurements):
    imageWidth = image.shape[1]

    pixelsPerMeasurement = int(imageWidth / (numberOfMeasurements + 1))

    for i in range(numberOfMeasurements):
        image = GetDiameterFromWidthPosition(image, int(pixelsPerMeasurement * (i + 1)))


    return image


def GetDiameterFromWidthPosition(image, imagePositionWidth):
    imageHeight = image.shape[0]

    filamentTopPosition = 0
    filamentBottomPosition = 0

    for i in range(imageHeight):
        b, g, r = image[i, imagePositionWidth]

        if(r == 255 and g == 0 and b == 0):
           filamentTopPosition = i + contourLineWidth
           break

    for i in range(imageHeight - 1, -1, -1):
        b, g, r = image[i, imagePositionWidth]

        if(r == 255 and g == 0 and b == 0):
           filamentBottomPosition = i - contourLineWidth
           break

    image = cv2.line(image, (imagePositionWidth, filamentTopPosition), (imagePositionWidth, filamentBottomPosition), (0, 255, 0), 1)
    
    image = cv2.putText(image, str(filamentBottomPosition - filamentTopPosition) + 'px', (int(imagePositionWidth + 5), int(imageHeight / 2)), cv2.QT_FONT_NORMAL, 1, (255, 0, 0), 1, cv2.LINE_AA)
    image = cv2.putText(image, str(round((filamentBottomPosition - filamentTopPosition) / pixelsPerMilimeter, 3)) + 'mm', (int(imagePositionWidth + 5), int((imageHeight / 2) + 50)), cv2.QT_FONT_NORMAL, 1, (255, 0, 0), 1, cv2.LINE_AA)
    
    return image