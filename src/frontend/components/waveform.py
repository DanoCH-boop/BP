import customtkinter
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np


class Waveform(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.segments = []
        self.images = []
        self.removed_indexes = []
        self.selected = None
        self.canvas_height = 250
        self.canvas_width = 915
        self.normal_fill = "#2cbe79" # green
        self.canvas = tk.Canvas(self, highlightthickness=0, background=("#dbdbdb"),
                               height=self.canvas_height)
        self.scrollbar = customtkinter.CTkScrollbar(self, orientation="horizontal")
        self.canvas.pack(expand=True, fill="both", padx=5, pady=(5, 0))
        self.scrollbar.pack(expand=True, fill="both", padx=5, pady=(0, 2))
        

    # https://stackoverflow.com/a/54645103
    def prepare_images(self, x1, y1, x2, y2, **kwargs):
        """
        Prepares the image for the speech segment
        """
        alpha = int(kwargs.pop('alpha') * 255)
        fill = kwargs.pop('fill')
        orange_color = (250, 135, 35)
        fill = orange_color + (alpha,)
        image = Image.new('RGBA', (int(x2 - x1) + 1, int(y2 - y1) + 1), fill)
        self.images.append(ImageTk.PhotoImage(image))

    def create_speech_rectangles(self, d1, d2, wav_num):
        """
        Creates the image, text and outlined rectangle for each segment
        """
        indices = np.where((d2 >= self.segments[:, 0]) & (d1 <= self.segments[:, 1]))[0]
        y0 = 0
        y1 = self.canvas_height
        for id in indices:
            outline = "orange"
            if id + 1 in self.removed_indexes and wav_num == 1:
                outline = "red"
            x = self.segments[id] - d1
            tags = ("speech", str(id))
            self.canvas.create_image(x[0], y0, image=self.images[id], anchor='nw', tags=tags)
            self.canvas.create_text(x[0] + (x[1] - x[0]) / 2, y1 / 2, text=str(int(tags[1]) + 1), tags=tags,
                                   fill="white",
                                   font=customtkinter.CTkFont(size=25, weight="bold"))
            self.canvas.create_rectangle(x[0], y0, x[1], y1, outline=outline, tags=tags)
            if str(id) == self.selected:
                self.canvas.create_image(x[0], y0, image=self.images[id], anchor='nw', tags=tags)
                self.canvas.create_text(x[0] + (x[1] - x[0]) / 2, y1 / 2, text=str(int(tags[1]) + 1), tags=tags,
                                       fill="white",
                                       font=customtkinter.CTkFont(size=25, weight="bold"))
                self.canvas.create_rectangle(x[0], y0, x[1], y1, outline=outline, tags=tags)

    