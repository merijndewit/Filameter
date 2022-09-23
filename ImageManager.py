from re import X
from PIL import Image
from PIL import ImageTk as itk
import cv2

def GetImageTK(image):
    return itk.PhotoImage(image)

def CV2ToTKAndResize(image, scale):
    sizeX = int(image.shape[1] * scale)
    sizeY = int(image.shape[0] * scale)
    resizedImage = cv2.resize(image, (sizeX, sizeY))
    return itk.PhotoImage(CV2ToPIL(resizedImage))

def CV2ToTKAndResize(image, width, height):
    resizedImage = cv2.resize(image, (width, height))
    return itk.PhotoImage(CV2ToPIL(resizedImage))

def PILToTKAndResize(image, width, height):
    resizedImage = image.resize((width, height))
    return itk.PhotoImage(resizedImage)

def CV2ToPIL(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pilImage = Image.fromarray(img)
    return pilImage

def GetEmptyImage():
    return Image.new("RGB",(800,200), (100, 100, 100))