import cv2
import os

thresholdValue = 140 #value between 0 and 255

def ProcessImage():
    img = GetGrayscaleCapturedImage()
    threshold = GetThresholdImage(img)
    contourImage = DrawContours(GetContours(threshold), GetCapturedImage())
    WriteImage(contourImage, "contourImage")
    WriteImage(threshold, "processedImage")

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
    cv2.drawContours(imageToDrawOn, contours, -1, (0, 0, 255), 2)
    return imageToDrawOn