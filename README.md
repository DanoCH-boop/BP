# BP - Bachelor's Thesis

### Name
- Tool for Automatic Subtitle Alignment

### Supervisor
- Ing. Tomáš Milet, Ph.D.

### Author
- Daniel Chudý

### Place
- FIT BUT, Brno

### Year
- 2023

## Subtitle aligner
- aligns subtitles for different versions of video files

### Description
- SubAligner is a python application that works on tkinter and uses ffmpeg to align subtitles for different vestion of video files

### Requirements
- python 3.10.8
- ffmpeg installation
- other requirements in ```requirements.txt``` file located in this folder

### FFmpeg installation
- Windows -- https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/
- Mac -- ```brew install ffmpeg```
- Linux -- ```sudo apt install ffmpeg```

### Launching app

#### Windows
- click on ```start.bat``` file in the app folder or navigate to ```app\startup\startup.exe``` and run the .exe file

#### Linux and Mac
- run ```pip install -r requirements.txt```
- make sure your python installation comes with Tkinter or install it manually
- go to the ```src``` folder and run ```startup.py``` like so: ```python startup.py```

### Usage
- run the app and input two MP4 files, and one SRT subtitle file
- click ```Align``` -- new subtitle file is created that fits the second Mp4 file
- the new subtitle file has the same name as the second Mp4 File and is automatically saved in the same folder

#### Input
- 2x Mp4 file
- SRT file that fits the first Mp4 file

#### Output 
- SRT file that fits the second Mp4 file