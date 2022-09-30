# Welcome to Filameter!
Filameter is a python program that runs on the raspberry pi to measure the diameter of filement. This can be used to measure filament that goes into a 3d printer, or filament that comes out of a filament extruder. This is just one of the ways to measure filament and i created this project to see if it was possible to do with a camera. The program is made to work with a small touchscreen but can also be used with a mouse.

<img alt="Filameter image" src="https://drive.google.com/uc?export=download&id=1zxoBXRyONYvGEvSm6Lw1VYAaBtUfH7Pm">
(a picture of the program running on a raspberry pi)

## Software
### Filament view
<img alt="Filameter image" src="https://drive.google.com/uc?export=download&id=1iwvX0y1FmgP-avLOkKxec1EYdPiBv3vN">
When recording or processing an image the result will be shown on the top left of the screen like the image above. With this you will be able to see what the program sees as filament. This also helps you to see if the filament gets out of frame, out of focus or if the threshold value is wrong.

### Graph
<img alt="Filameter image" src="https://drive.google.com/uc?export=download&id=18DdQdnAPKlVC_yRboTSC0K5O4MW3v_5Q">
The graph can quickly show you how consistent the filament is over a single capture or recording. The graph adjusts itself so that all the lines will always be visible.

>Note: Graph only works when there is more than one measurement per capture or when recording.

### Filament info
<img alt="Filameter image" src="https://drive.google.com/uc?export=download&id=1NZ4uAromzrBUk7p8D-QvTNNPXZs_Onge">

The filament info shows information of a single capture. 

>Note: Tolerance only works when there is more than one measurement per capture.

### Record
Recording will keep track of the diameter of the filament until the recording is stopped by the user. A capture will be made every x amount of seconds and will be shown on the graph and also saved. When a recording is stopped a json file will be made with the recording info. In this json file you will find the following information: 
- Average diameter over the entire recording
- max measured diameter
- min measured diameter
- average of multiple measurements

### Single actions
<img alt="Filameter image" src="https://drive.google.com/uc?export=download&id=1ebCNQf6Jhz2EzOqdEPm5BpMIU84l2m08">

With single actions you can calibrate your settings, focus your camera and other preperations.

### Settings 
<img alt="Filameter image" src="https://drive.google.com/uc?export=download&id=1CodFPf4kUzvE9dzSNpODCn32ookZqqvT">
In settings you can adjust the following settings:

- number of measurements
- threshold
- border offset
- pixels per mm
- image processing type (opencv or filameter's own way)
- camera capture width
- capera capture height

If you want to adjust one of the settings you can simply click on the setting and it will appear light blue. Then on the control pad you can adjust the value. Select the amount you want that setting to change and then with the + or - you can either subtract or add that value to the setting.

<img alt="Filameter image" src="https://drive.google.com/uc?export=download&id=1aDW4zCg5n1p714PXtwvR5lt36ky0skOI">

## Hardware
For this program you need the following hardware:

- Raspberry pi
- hq camera sensor for the raspberry pi
- microscope lens
- small led strip
- (optional) touchscreen

As a housing feel free to use whatever you want!

I made a funny housing with my 3d printer as an example:

<img alt="Filameter image" src="https://drive.google.com/uc?export=download&id=1u0V9BamwiZUjQ35yPsmngdh9vHvC0Zog">

<img alt="Filameter image" src="https://drive.google.com/uc?export=download&id=11OZkCyprDH-BDeD0lqOu0FyZLDbyiZSQ">
