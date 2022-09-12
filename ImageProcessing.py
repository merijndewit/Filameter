import cv2
import os

thresholdValue = 110 #value between 0 and 255
minObjectSize = 8000

def ProcessImage():
    img = GetGrayscaleCapturedImage()
    threshold = GetThresholdImage(img)
    contourImage = DrawContours(GetContours(threshold), cv2.cvtColor(GetGrayscaleCapturedImage(), cv2.COLOR_GRAY2BGR))
    contourImageWithDiameter = CountPixelsInDiameter(contourImage)
    WriteImage(contourImageWithDiameter, "contourImage")
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
            cv2.drawContours(imageToDrawOn, contour, -1, (0, 0, 255), 2)
    
    return imageToDrawOn

def CountPixelsInDiameter(image):
    imageHeight = image.shape[0]
    imageWidth = image.shape[1]

    filamentTopPosition = 0
    filamentBottomPosition = 0

    for i in range(imageHeight):
        b, g, r = image[i, int(imageWidth / 2)]

        if(r == 255 and g == 0 and b == 0):
           filamentTopPosition = i
           break

    for i in range(imageHeight - 1, -1, -1):
        b, g, r = image[i, int(imageWidth / 2)]

        if(r == 255 and g == 0 and b == 0):
           filamentBottomPosition = i
           break

    imageWithLine = cv2.line(image, (int(imageWidth / 2), filamentTopPosition), (int(imageWidth / 2), filamentBottomPosition), (0, 255, 0), 2)
    return imageWithLine