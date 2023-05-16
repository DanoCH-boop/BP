from frontend.app import App
import sys
from tkinter.messagebox import showerror

# check if ffmpeg is installed
# Six, edited by j3h, https://stackoverflow.com/a/34177358
from shutil import which

if(which("ffmpeg") is None):
    showerror("Error", 
              "FFmpeg is not installed!\nInstallation tutorial in Readme.md\n")
    exit(1)

app = App()
app.mainloop()
# kill all daemon threads if align goes wrong
sys.exit()
