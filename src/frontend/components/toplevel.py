import customtkinter
import tkinter as tk
from PIL import Image, ImageTk
from itertools import count, cycle


# https://pythonprogramming.altervista.org/animate-gif-in-tkinter/
class ImageLabel(tk.Label):
    """
    A Label that displays images, and plays them if they are gifs
    :im: A PIL Image instance or a string filename
    """

    def load(self, im):
        """Load the image into the frame"""
        if isinstance(im, str):
            im = Image.open(im)
        frames = []

        try:
            for i in count(1):
                frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass
        self.frames = cycle(frames)

        try:
            self.delay = im.info['duration']
        except:
            self.delay = 100

        if len(frames) == 1:
            self.config(image=next(self.frames))
        else:
            self.next_frame()

    def unload(self):
        self.config(image=None)
        self.frames = None

    def next_frame(self):
        """Animation handler"""
        if self.frames:
            # try:
            self.config(image=next(self.frames))
            # except:
            #     return
            self.after(self.delay, self.next_frame)


class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, mode, *args, **kwargs):
        super().__init__(*args, **kwargs)
        w = 300  # Width
        h = 150  # Height
        # https://coderslegacy.com/tkinter-center-window-on-screen/
        screen_width = self.winfo_screenwidth()  # Width of the screen
        screen_height = self.winfo_screenheight()  # Height of the screen
        screen_width, screen_height = 1920, 1080
        # Calculate Starting X and Y coordinates for Window
        x = (screen_width / 2) - (w / 2)
        y = (screen_height / 2) - (h / 2)

        self.geometry('%dx%d+%d+%d' % (w, h, x, y))

        bg = "#ebebeb"
        img = "../icons/loading_light.gif"
        if mode == 1:
            bg = "#242424"
            img = "../icons/loading_dark.gif"
        self.title("Generating waveform")
        self.label = customtkinter.CTkLabel(self, text="Generating waveform...", font=customtkinter.CTkFont(size=16))
        self.image = ImageLabel(self, bg=bg)
        self.label.pack(padx=20, pady=20)
        self.image.pack(padx=20, pady=(0, 20))
        self.image.load(img)
