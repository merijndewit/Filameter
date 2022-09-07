import cv2
import os

thresholdValue = 120 #value between 0 and 255

def ProcessImage():
    img = cv2.imread(os.path.dirname(os.path.realpath(__file__)) + "/CapturedImages/capture.png", cv2.IMREAD_GRAYSCALE)
    _, threshold = cv2.threshold(img, thresholdValue, 255, cv2.THRESH_BINARY)

    #cv2.imshow("grayscale", img)
    #cv2.imshow("threshold", threshold)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

    if not cv2.imwrite("CapturedImages/processedImage.png", threshold):
        raise Exception("Could not write image")