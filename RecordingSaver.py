import json

def SaveFilamentRecordingToJSON(filamentRecording):
    jsonString = json.dumps(filamentRecording.__dict__)
    print(jsonString)