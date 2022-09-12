from re import X
from PIL import Image
from PIL import ImageTk as itk

def GetImageTK(path, size):
    image1 = Image.open(path)
    resizedImage = image1.resize(size)
    return itk.PhotoImage(resizedImage)

def GetImageAndResizeTK(path, scale):
    image1 = Image.open(path)
    sizeX = int(image1.size[0] * scale)
    sizeY = int(image1.size[1] * scale)
    resizedImage = image1.resize((sizeX, sizeY))
    return itk.PhotoImage(resizedImage)