class MainWindow():
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

        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../icons")
        self.add_icon = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "add_dark.png")),
                                               dark_image=Image.open(os.path.join(image_path, "add_light.png")),
                                               size=(50, 50))
        self.play_icon = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "play_button.png")),
                                                size=(20, 20))
        self.pause_icon = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "pause_button.png")),
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
        """ updates the duration after finding the duration """
        duration = self.video.video_info()["duration"]
        self.end_time.configure(text=str(datetime.timedelta(seconds=duration)).rsplit(".")[0])
        self.slider.configure(to=duration)
        print(duration)

    def seek(self, val):
        print("seeked to:", int(val))
        self.video.seek(math.ceil(val))
        if self.video.is_paused():
            self.video.play()
            self.video.pause()

    def play_pause(self):
        if self.video.is_paused():
            print("paused")
            self.video.play()
            self.play_button.configure(image=self.pause_icon)
            return
        print("not paused")
        self.video.pause()
        self.play_button.configure(image=self.play_icon)

    def update_slider(self, event):
        dur = self.video.current_duration()
        self.slider.set(dur)
        self.end_time.configure(text=str(datetime.timedelta(seconds=dur)).rsplit(".")[0])

    def video_ended(self, event):
        self.slider.set(0)
        self.play_button.configure(image=self.play_icon)

    def video_setup(self, appearance, filename):
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
