from tkinter import Tk  
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo
import os

def openfiles():
    Tk().withdraw() # no root window appears
    showinfo("Dialog","Select two Mp4 files")
    filename1 = askopenfilename(filetypes=(('Mp4 files', '*.mp4'),('All files', '*.*')), initialdir=os.getcwd())
    showinfo("Dialog",f"First file selected:\n{filename1.split('/')[-1]}")
    print(filename1)
    # srtfilename = askopenfilename(filetypes=(('SRT files', '*.srt'),('All files', '*.*')), initialdir=os.getcwd()) 
    # showinfo("Dialog",f"First file selected:\n{srtfilename.split('/')[-1]}")
    # print(srtfilename)
    filename2 = askopenfilename(filetypes=(('Mp4 files', '*.mp4'),('All files', '*.*')), initialdir=filename1)
    showinfo("Dialog",f"Files selected:\n\n\t{filename1.split('/')[-1]}\n\t{filename2.split('/')[-1]}\n\nClick Ok to proceed with subititle aligning.")
    print(filename2)
    return filename1, filename2