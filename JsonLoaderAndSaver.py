from datetime import datetime
import json

def SaveFilamentRecordingToJSON(filamentRecording):
    with open("FilamentRecordings/FilamentRecording_" + str(datetime.now()) +".json", "w") as jsonFile:
        jsonFile.write(filamentRecording.toJSON())

def SaveObjectToJSON(object, name):
    with open(str(name) +".json", "w") as jsonFile:
        jsonFile.write(json.dumps(object, indent=4, default=lambda x: x.__json__))

def GetJSON(name):
    with open(str(name) +".json", "r") as jsonFile:
        return json.load(jsonFile)
