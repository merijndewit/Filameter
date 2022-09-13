import time

startTime = 0

def StartTimer():
    global startTime
    startTime = time.time()

def StopTimer(taskName):
    takenTime = time.time() - startTime
    print(str(taskName) + " took: " + str(takenTime))
    return takenTime