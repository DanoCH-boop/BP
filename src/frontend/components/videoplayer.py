import customtkinter
import datetime
import math
from PIL import Image
import os
from tkVideoPlayer import TkinterVideo


class VideoPlayer(customtkinter.CTkFrame):
    def __init__(self, *args,
                        mas = any,
                        rw = any,
                  **kwargs):
        super().__init__(*args, **kwargs)

        self.mas = mas
        self.rw = rw

        self.pady = 0
        if self.rw == 3:
            self.pady = (0, 10)

        self.add_icon = customtkinter.CTkImage(light_image=Image.open("../icons/add_dark.png"),
                                               dark_image=Image.open("../icons/add_light.png"),
                                               size=(50, 50))
        self.play_icon = customtkinter.CTkImage(light_image=Image.open("../icons/play_button.png"),
                                                size=(20, 20))
        self.pause_icon = customtkinter.CTkImage(light_image=Image.open("../icons/pause_button.png"),
                                                 size=(20, 20))
        
        self.video = "not_setup"
        self.addvid = customtkinter.CTkButton(self, text="Add Mp4 file",
                                               image=self.add_icon,
                                               fg_color="transparent", hover_color=("gray70", "gray30"),
                                               text_color=("gray10", "gray90"),
                                               compound="top")
        self.addvid.pack(fill="both", expand=True, padx=2, pady=2)
        self.seeker = customtkinter.CTkFrame(self.mas, fg_color="transparent", corner_radius=10, width=140,
                                              height=28)
        self.seeker.grid(row=self.rw, column=0, sticky="nsew", pady=self.pady, padx=(10, 0))
        self.slider = customtkinter.CTkSlider(self.seeker, from_=0, to=1, command=self.seek, height=15)
        self.slider.set(0)
        self.slider.configure(state="disabled")
        self.play_button = customtkinter.CTkButton(self.seeker, image=self.play_icon, text="", fg_color="transparent",
                                                    hover_color=("gray70", "gray30"),
                                                    command=self.play_pause, width=28)
        self.play_button.configure(state="disabled")
        self.end_time = customtkinter.CTkLabel(self.seeker, text="00:00:00")
        self.end_time.grid(row=0, column=2, pady=(2, 2))

        self.slider.grid(row=0, column=1, sticky="ew", pady=(2, 2))
        self.play_button.grid(row=0, column=0, sticky="nsew", padx=(3, 3), pady=(2, 2))
        self.seeker.grid_columnconfigure(1, weight=8)

    def update_duration(self, event):
        """ Updates the duration after finding the duration """
        duration = self.video.video_info()["duration"]
        self.end_time.configure(text=str(datetime.timedelta(seconds=duration)).rsplit(".")[0])
        self.slider.configure(to=duration)
        print(duration)

    def seek(self, val):
        """Seeks to a given second in the video"""
        if self.video == "not_setup":
            return
        print("seeked to:", int(val))
        self.video.seek(math.ceil(val))
        # if self.video._paused:
        #     self.video.play()
        #     self.video.pause()

    def play_pause(self):
        """Pauses and/or plays the video according to the previous state"""
        if self.video.is_paused():
            print("paused")
            self.video.play()
            self.play_button.configure(image=self.pause_icon)
            return
        print("not paused")
        self.video.pause()
        self.play_button.configure(image=self.play_icon)

    def update_slider(self, event):
        """Updates the video slider"""
        dur = self.video.current_duration()
        self.slider.set(dur)
        self.end_time.configure(text=str(datetime.timedelta(seconds=dur)).rsplit(".")[0])

    def video_ended(self, event):
        """Handles the ending of a video"""
        self.slider.set(0)
        self.play_button.configure(image=self.play_icon)

    def video_setup(self, appearance, filename):
        """Sets up the video after choosing a video file and binds the video to events"""
        bg = "#dbdbdb"
        fg = "black"
        if appearance == 1:
            bg = "#2b2b2b"
            fg = "white"
        self.play_button.configure(state="normal")
        self.slider.configure(state="normal")
        self.slider.set(0)
        self.play_button.configure(image=self.play_icon)
        self.addvid.pack_forget()
        if self.video != "not_setup":
            self.video.pack_forget()
        self.video = TkinterVideo(self, fg=fg, background=bg, text="Click play to play video!",
                                   font=customtkinter.CTkFont(size=20), keep_aspect=True)
        self.video.load(filename)
        self.video.pack(fill="both", expand=True, padx=4, pady=2)
        # self.video1.set_size((600, 450)) # sets the frame size
        self.video.bind("<<Duration>>", self.update_duration)
        self.video.bind("<<SecondChanged>>", self.update_slider)
        self.video.bind("<<Ended>>", self.video_ended)

# Author Paul

# MIT License
#
# Copyright (c) 2021 Paul
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.