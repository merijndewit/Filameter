def GetAverageFromReadings(readings):
    average = 0
    for i in range(len(readings)):
        average += readings[i]

    return (average / len(readings))

def GetToleranceFromReadings(readings):
    maxReading = max(readings)
    minReading = min(readings)

    return (maxReading - minReading) / 2

