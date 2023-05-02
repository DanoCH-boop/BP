import customtkinter
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
from misc.speech_segments import get_speech_segments


class Waveform(customtkinter.CTkFrame):
    def __init__(self, *args, mode, other_frame, video, srt_fname, fname, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = mode
        self.tkvideo = video
        self.sub = "not_setup"
        self.segments = []
        self.images = []
        self.grouped = []
        self.signal_mismatch = np.array([])
        self.removed_indexes = []
        self.selected = None
        self.canvas_height = 250
        self.canvas_width = 915
        self.x_coords = []
        self.y_coords = []
        self.srt_fname = srt_fname
        self.fname = fname
        self.other_frame = other_frame
        self.sr = 0
        self.normal_fill = "#2cbe79" # green
        self.removed_fill = "#db3737"  # red
        self.canvas = tk.Canvas(self, highlightthickness=0, background=("#dbdbdb"),
                               height=self.canvas_height)
        self.scrollbar = customtkinter.CTkScrollbar(self, orientation="horizontal")
        self.canvas.pack(expand=True, fill="both", padx=5, pady=(5, 0))
        self.scrollbar.pack(expand=True, fill="both", padx=5, pady=(0, 2))
    
    def gen_wav(self):
        self.scrollbar.set(0, 1 / (len(self.y_coords) / 1000))
        self.draw_waveform()

    def draw_waveform(self, *args):
        """Draws the waveform in the second_frame canvas based on the current scrollbar position and 
        creates rectangles for the speech segments.
        """
        if self.fname == "":
            return
        self.canvas.delete("all")
        l1, _ = self.scrollbar.get()
        d1 = int(len(self.y_coords) * l1)
        d2 = d1 + self.canvas_width * 10
        self.canvas.create_line(*zip(self.x_coords, (self.canvas_height / 2 - self.y_coords[d1:d2])),
                                fill=self.normal_fill)
        if self.srt_fname == "":
            return
        self.create_speech_rectangles(d1 / 10, d2 / 10)
        # only waveform 2, if i didnt actually implement the other click-over variant <
        indices = np.where((d2 >= self.signal_mismatch) & (d1 <= self.signal_mismatch))[0]
        for i in indices:
            x = (self.signal_mismatch[i] - d1) / 10
            self.canvas.create_rectangle(x, 0, x + 5, self.canvas_height, fill=self.removed_fill,
                                         outline=self.removed_fill, tags=("removed", str(i)))
        # > only waveform 2, if i didnt actually implement the other click-over variant

    # acw1668, https://stackoverflow.com/a/54645103
    def prepare_images(self, x1, y1, x2, y2, **kwargs):
        """
        Prepare images for the speech segment
        """
        alpha = int(kwargs.pop('alpha') * 255)
        orange_color = (250, 135, 35)
        fill = orange_color + (alpha,)
        image = Image.new('RGBA', (int(x2 - x1) + 1, int(y2 - y1) + 1), fill)
        self.images.append(ImageTk.PhotoImage(image))

    def create_speech_rectangles(self, d1, d2):
        """
        Creates the image, text and outlined rectangle for each segment
        """
        indices = np.where((d2 >= self.segments[:, 0]) & (d1 <= self.segments[:, 1]))[0]
        y0 = 0 
        y1 = self.canvas_height
        for id in indices:
            outline = "orange"
            if id + 1 in self.removed_indexes and self.mode == "in":
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

    def mark_speech_segments(self):
        """Prepares and displays the speech segments in the second waveform as images with transparency."""
        segments = get_speech_segments(self.srt_fname)
        self.segments = segments * (self.sr / 10)
        for seg in self.segments:
            self.prepare_images(seg[0], 0, seg[1], self.canvas_height, alpha=.5)
        # self.create_speech_rectangles(0, self.canvas_width, 2)
        self.canvas.tag_bind("speech", "<Button-1>", self.selected_speech_event)
        self.canvas.tag_bind("removed", "<Button-1>", self.selected_speech_event)

    def selected_speech_event(self, event):
        """Handles the click event on a speech segment in the second waveform and highlights the corresponding 
        segment in the waveform and scrolls to and highlights the corresponding segment in the aligned subtitles.
        """
        item = event.widget.find_withtag('current')
        tags = self.canvas.itemcget(item, "tags")
        id = tags.split(" ")[1]

        print(tags)
        # if a deleted segment is selected (the scene missing from the second video)
        # scroll to segment in first waveform
        if self.mode == "out":
            if tags.split(" ")[0] == "removed":
                # get the first deleted subtitle
                id_del = self.other_frame.grouped[int(id)][0]
                x0, x1 = self.other_frame.segments[int(id_del) - 1]
                img_width = x1 - x0
                # offset to make the selected segment appear in the middle of the canvas
                offset = (self.canvas_width - img_width) / 2
                scroll = (x0 - offset) / (len(self.y_coords) / 10)
                self.other_frame.scrollbar.set(scroll, scroll)
                self.other_frame.draw_waveform()
                return

        # scroll to deleted
        if self.mode == "in":
            try:
                print("id", int(id) + 1)
                index = np.where([int(id) + 1 in subarr for subarr in self.grouped])[0]
                offset = self.canvas_width / 2 * 10
                scroll = (self.other_frame.signal_mismatch[index] - offset) / len(self.y_coords)
                print("scroll", scroll)
                self.other_frame.scrollbar.set(scroll, scroll)
                self.other_frame.draw_waveform()
            except:
                pass
        
        self.selected = id

        self.highlight_selected(id)

        # scroll to subs
        self.sub.see(id + ".first")
        line = self.sub.dlineinfo(id + ".first")
        better_offset = 10  # for better visual
        self.sub.yview_scroll(line[1] - better_offset, 'pixels')


    def highlight_selected(self, id):
        """Highlights the selected segment in the fisrt subtitles and seeks to the corresponding time in the first video."""
        print("highlighting" + id)

        self.draw_waveform()

        # seek in video 
        x0, _ = self.segments[int(id)]
        if self.tkvideo.video != "not_setup":
            self.tkvideo.seek(x0 * 10 / self.sr)

        self.sub.highlight_sub(id)
