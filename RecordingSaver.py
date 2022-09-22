from datetime import datetime

def SaveFilamentRecordingToJSON(filamentRecording):
    with open("FilamentRecordings/FilamentRecording_" + str(datetime.now()) +".json", "w") as jsonFile:
        jsonFile.write(filamentRecording.toJSON())