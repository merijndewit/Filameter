from PIL import Image
from PIL import ImageTk as itk

def GetImageTK(path, size):
    image1 = Image.open(path)
    resizedImage = image1.resize(size)
    return itk.PhotoImage(resizedImage)