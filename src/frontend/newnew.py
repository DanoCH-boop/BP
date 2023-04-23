import customtkinter
import numpy as np
from tkinter.messagebox import showinfo
import tkinter as tk
from tkinter.filedialog import askopenfilename
import os
from misc.convert import convert
from align import align
from misc.speech_segments import get_speech_segments
from tkVideoPlayer import TkinterVideo
import math
import pysrt
import sys
from PIL import Image, ImageTk
import datetime
import threading
from toplevel import ToplevelWindow

customtkinter.set_default_color_theme("green")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Subtitle aligner v0.1")
        self.geometry("1000x600")
        self.minsize(1000, 600)
        # self.geometry("%dx%d+0+0" % (self.winfo_screenwidth(), self.winfo_screenheight()-60))
        self.toplevel_window = None

        # color map
        self.cm = {
            "fr_bg_d": "#2b2b2b",  # frame_background_dark
            "hl_d": "#925827",  # highlight dark
            "vid_bg_d": "#242424",  # video background dark
            "fr_bg_l": "#dbdbdb",  # frame background light
            "hl_l": "#eab17f",  # highlight light
            "vid_bg_l": "#ebebeb"  # video background
        }

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        srtfilename = ""
        filename1 = ""
        filename2 = ""
        fname = ""

        # srtfilename = "../example/example.srt"
        # filename1 = "../example/example.wav"
        # filename2 = "../example/example_trim.wav"

        self.srtfilename = srtfilename
        self.filename1 = filename1
        self.filename2 = filename2
        self.fname = fname

        self.example_loaded = 1

        self.removed_fill = "#db3737"  # red
        self.normal_fill = "#2cbe79"  # green

        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../icons")
        self.mp4_icon = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "mp4add_ico_dark.png")),
                                               dark_image=Image.open(os.path.join(image_path, "mp4add_ico_light.png")),
                                               size=(65, 65))
        self.srt_icon = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "srtadd_ico_dark.png")),
                                               dark_image=Image.open(os.path.join(image_path, "srtadd_ico_light.png")),
                                               size=(65, 65))
        self.add_icon = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "add_dark.png")),
                                               dark_image=Image.open(os.path.join(image_path, "add_light.png")),
                                               size=(50, 50))
        self.play_icon = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "play_button.png")),
                                                size=(20, 20))
        self.pause_icon = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "pause_button.png")),
                                                 size=(20, 20))

        # create menu frame
        self.sidebar_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        self.sidebar_frame_label = customtkinter.CTkLabel(self.sidebar_frame, text="SubAligner",
                                                          compound="left",
                                                          font=customtkinter.CTkFont(size=20, weight="bold"))
        self.sidebar_frame_label.grid(row=0, column=0, padx=40, pady=20)

        self.chooseFile_btn1 = customtkinter.CTkButton(self.sidebar_frame, corner_radius=10, height=10,
                                                       border_spacing=0, text="Mp4 File 1",
                                                       fg_color="transparent", text_color=("gray10", "gray90"),
                                                       hover_color=("gray70", "gray30"),
                                                       image=self.mp4_icon, anchor="w",
                                                       command=self.chooseFile_btn1_event)
        self.chooseFile_btn1.grid(row=1, column=0, pady=0)

        self.chooseFile_btn2 = customtkinter.CTkButton(self.sidebar_frame, corner_radius=10, height=10,
                                                       border_spacing=0, text="Mp4 File 2",
                                                       fg_color="transparent", text_color=("gray10", "gray90"),
                                                       hover_color=("gray70", "gray30"),
                                                       image=self.mp4_icon, anchor="w",
                                                       command=self.chooseFile_btn2_event)
        self.chooseFile_btn2.grid(row=2, column=0, pady=0)

        self.choose_srtFile = customtkinter.CTkButton(self.sidebar_frame, corner_radius=10, height=10, border_spacing=0,
                                                      text="SRT File",
                                                      fg_color="transparent", text_color=("gray10", "gray90"),
                                                      hover_color=("gray70", "gray30"),
                                                      image=self.srt_icon, anchor="w",
                                                      command=self.choose_srtFile_event)
        self.choose_srtFile.grid(row=3, column=0, pady=0)

        self.clear_btn = customtkinter.CTkButton(self.sidebar_frame, text="Clear", width=100, height=40,
                                                 font=customtkinter.CTkFont(size=15), command=self.clear_window)
        self.clear_btn.grid(row=4, column=0, pady=10, sticky="n")

        # initiate "aligned" button
        self.align_button = customtkinter.CTkButton(self.sidebar_frame, text="Align", width=100, height=40,
                                                    font=customtkinter.CTkFont(size=15), command=self.align_event,
                                                    state="disabled")
        self.align_button.grid(row=6, column=0, pady=10)

        # Initiate "Subtitles Aligned!" label
        self.aligned_text = customtkinter.CTkLabel(self.sidebar_frame, text="")
        self.aligned_text.grid(row=7, column=0, pady=(0, 10))

        # theme switch
        self.appearance_mode_menu = customtkinter.CTkSwitch(self.sidebar_frame,
                                                            command=self.change_appearance_mode_event, text="Dark mode",
                                                            switch_height=15, switch_width=35)
        self.appearance_mode_menu.grid(row=9, column=0, padx=20, pady=(10, 20), sticky="s")

        # create main frame
        self.main_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", pady=0, padx=0)
        self.main_frame.columnconfigure(1, weight=3)
        self.main_frame.columnconfigure(0, weight=2)

        # create subs frame
        self.subs_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.subs_frame.grid(row=1, column=1, sticky="sew", pady=(0, 5), padx=0)
        self.subs_frame.grid_rowconfigure(0, weight=1)
        self.subs_frame.grid_columnconfigure(0, weight=1)
        self.subs_frame.grid_columnconfigure(1, weight=1)

        self.init_mainWindow()
        self.state("zoomed")

    def init_mainWindow(self):
        self.canvas_height = 250
        self.canvas_width = 915
        self.signal_mismatch = np.array([])
        self.removed_indexes = []
        self.x_coords = np.arange(0, self.canvas_width, 0.1)
        self.y_coords = []
        self.y_coords2 = []
        self.previous_tag2 = None
        self.selected = None
        self.previous_tag2A = None
        self.selectedA = None
        self.offset = 0

        # init videos
        self.tkvideo1 = customtkinter.CTkFrame(self.main_frame, fg_color=("#dbdbdb", "#2b2b2b"), corner_radius=10,
                                               width=140)
        self.tkvideo1.grid(row=0, column=0, sticky="nsew", pady=(10, 0), padx=(10, 0))
        self.addvid1 = customtkinter.CTkButton(self.tkvideo1, text="Add Mp4 file", command=self.chooseFile_btn1_event,
                                               image=self.add_icon,
                                               fg_color="transparent", hover_color=("gray70", "gray30"),
                                               text_color=("gray10", "gray90"),
                                               compound="top")
        self.addvid1.pack(fill="both", expand=True, padx=2, pady=2)
        self.seeker1 = customtkinter.CTkFrame(self.main_frame, fg_color="transparent", corner_radius=10, width=140,
                                              height=28)
        self.seeker1.grid(row=1, column=0, sticky="nsew", pady=0, padx=(10, 0))
        self.slider1 = customtkinter.CTkSlider(self.seeker1, from_=0, to=1, command=self.seek1, height=15)
        self.slider1.set(0)
        self.slider1.configure(state="disabled")
        self.play_button1 = customtkinter.CTkButton(self.seeker1, image=self.play_icon, text="", fg_color="transparent",
                                                    hover_color=("gray70", "gray30"),
                                                    command=self.play_pause1, width=28)
        self.play_button1.configure(state="disabled")
        self.end_time1 = customtkinter.CTkLabel(self.seeker1, text="00:00:00")
        self.end_time1.grid(row=0, column=2, pady=(2, 2))

        self.slider1.grid(row=0, column=1, sticky="ew", pady=(2, 2))
        self.play_button1.grid(row=0, column=0, sticky="nsew", padx=(3, 3), pady=(2, 2))
        self.seeker1.grid_columnconfigure(1, weight=8)
        self.video1 = "not_setup"

        self.tkvideo2 = customtkinter.CTkFrame(self.main_frame, fg_color=("#dbdbdb", "#2b2b2b"), corner_radius=10,
                                               width=140)
        self.tkvideo2.grid(row=2, column=0, sticky="nsew", pady=(5, 0), padx=(10, 0))
        self.addvid2 = customtkinter.CTkButton(self.tkvideo2, text="Add Mp4 file", command=self.chooseFile_btn2_event,
                                               image=self.add_icon,
                                               fg_color="transparent", hover_color=("gray70", "gray30"),
                                               text_color=("gray10", "gray90"),
                                               compound="top")
        self.addvid2.pack(fill="both", expand=True, padx=2, pady=2)
        self.seeker2 = customtkinter.CTkFrame(self.main_frame, fg_color="transparent", corner_radius=10, width=140,
                                              height=28)
        self.seeker2.grid(row=3, column=0, sticky="nsew", pady=(0, 10), padx=(10, 0))
        self.slider2 = customtkinter.CTkSlider(self.seeker2, from_=0, to=1, command=self.seek2, height=15)
        self.slider2.set(0)
        self.slider2.configure(state="disabled")
        self.play_button2 = customtkinter.CTkButton(self.seeker2, image=self.play_icon, text="", fg_color="transparent",
                                                    hover_color=("gray70", "gray30"),
                                                    command=self.play_pause2, width=28)
        self.play_button2.configure(state="disabled")
        self.end_time2 = customtkinter.CTkLabel(self.seeker2, text="00:00:00")
        self.end_time2.grid(row=0, column=2, pady=(2, 2))
        self.slider2.grid(row=0, column=1, sticky="ew", pady=(2, 2))
        self.play_button2.grid(row=0, column=0, sticky="nsew", padx=(3, 3), pady=(2, 2))
        self.seeker2.grid_columnconfigure(1, weight=8)
        self.video2 = "not_setup"

        # setup canvases for waveforms
        self.first_frame = customtkinter.CTkFrame(master=self.main_frame, fg_color=("#dbdbdb", "#2b2b2b"),
                                                  corner_radius=10)
        self.first_frame.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="nsew")
        self.first = tk.Canvas(self.first_frame, highlightthickness=0, background=("#dbdbdb"),
                               height=self.canvas_height)
        self.first_sbar = customtkinter.CTkScrollbar(self.first_frame, orientation="horizontal",
                                                     command=self.draw_waveform1)
        self.first.pack(expand=True, fill="both", padx=5, pady=(5, 0))
        self.first_sbar.pack(expand=True, fill="both", padx=5, pady=(0, 2))
        self.update()
        self.first.create_line(0, self.first.winfo_height() / 2, self.canvas_width, self.first.winfo_height() / 2,
                               fill=self.normal_fill)

        self.second_frame = customtkinter.CTkFrame(master=self.main_frame, fg_color=("#dbdbdb", "#2b2b2b"),
                                                   corner_radius=10)
        self.second_frame.grid(row=2, column=1, padx=10, pady=(5, 0), sticky="nsew")
        self.second = tk.Canvas(self.second_frame, highlightthickness=0, background=("#dbdbdb"),
                                height=self.canvas_height)
        self.second_sbar = customtkinter.CTkScrollbar(self.second_frame, orientation="horizontal",
                                                      command=self.draw_waveform2)
        self.second.pack(expand=True, fill="both", padx=5, pady=(5, 0))
        self.second_sbar.pack(expand=True, fill="both", padx=5, pady=(0, 2))
        self.update()
        self.second.create_line(0, self.second.winfo_height() / 2, self.canvas_width, self.second.winfo_height() / 2,
                                fill=self.normal_fill)

        # initiate subs frame
        self.orig_sub = customtkinter.CTkTextbox(self.subs_frame, corner_radius=10, text_color=("gray10", "gray90"),
                                                 height=260, wrap="none",
                                                 font=customtkinter.CTkFont(family="Consolas"))
        self.orig_sub.insert("0.0", "Original subtitles:")
        self.orig_sub.tag_add("Title", "1.0", "1.20")
        # self.orig_sub.tag_config("Title", font=customtkinter.CTkFont(weight="bold", size=16))
        self.orig_sub.grid(row=0, column=0, padx=10, pady=0, sticky="we")
        self.srt_add = customtkinter.CTkButton(self.orig_sub, text="Add SRT file", command=self.choose_srtFile_event,
                                               image=self.add_icon,
                                               fg_color="transparent", hover_color=("gray90", "gray30"),
                                               text_color=("gray10", "gray90"),
                                               compound="top")
        self.srt_add.place(relx=.5, rely=.5, anchor="c", relwidth=0.5, relheight=0.5)
        self.orig_sub.configure(state="disabled")

        self.aligned_sub = customtkinter.CTkTextbox(self.subs_frame, corner_radius=10, text_color=("gray10", "gray90"),
                                                    height=260, wrap="none",
                                                    font=customtkinter.CTkFont(family="Consolas"))
        self.aligned_sub.insert("0.0", "Aligned subtitles:\n")
        self.not_aligned_label = customtkinter.CTkLabel(self.aligned_sub, text="Subtitles not yet aligned!")
        self.not_aligned_label.place(relx=0.5, rely=0.5, anchor="c")
        self.aligned_sub.tag_add("Title", "1.0", "1.20")
        # self.aligned_sub.tag_config("Title", font=customtkinter.CTkFont(weight="bold", size=16))
        self.aligned_sub.grid(row=0, column=1, padx=10, pady=0, sticky="ew")
        self.aligned_sub.configure(state="disabled")

        self.orig_sub.tag_config("Removed", foreground=self.removed_fill, overstrike=True)
        self.align_button.configure(state="disabled")

    def _bound_to_mousewheel(self, event):
        self.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        if event.widget.winfo_id() == self.first.winfo_id():
            widget = self.first_sbar
            func = self.draw_waveform1
        elif event.widget.winfo_id() == self.second.winfo_id():
            widget = self.second_sbar
            func = self.draw_waveform2
        x, _ = widget.get()
        offset = -1 * (event.delta / 120) * 0.01
        scroll = x + offset
        if scroll < 0 or scroll > 1:
            if scroll < 0:
                widget.set(0, 0)
            else:
                widget.set(1, 1)
            func()
            return
        widget.set(scroll, scroll)
        func()

    def window_handler(self, func):
        self.toplevel_window = ToplevelWindow(mode=self.appearance_mode_menu.get())
        self.toplevel_window.focus()
        # start a new thread to run the event handling code
        t = threading.Thread(target=func)
        t.daemon = True
        t.start()

        # wait for the window to be destroyed before continuing
        self.toplevel_window.wait_window()

    def chooseFile_btn1_event(self):
        previous1 = self.filename1

        if self.example_loaded == 1:
            self.filename1 = askopenfilename(filetypes=(('Mp4, WAV files', '*.mp4;*.wav'), ('All files', '*.*')),
                                             initialdir=os.getcwd(), title="Choose first Mp4 file")

        if self.filename1 == "":
            self.filename1 = previous1
            return
        elif self.filename1.rsplit(".", 1)[1] not in ("mp4", "wav"):
            showinfo("Wrong file type", f"File \"{self.filename1.rsplit('/', 1)[-1]}\" is not an Mp4 or a Wav file!")
            return

        print(self.filename1)
        self.window_handler(self.generating_waveform1)

    def generating_waveform1(self):
        if self.filename1.rsplit(".", 1)[1] == "mp4":
            self.video1_setup()
        self.toplevel_window.focus()
        self.y_coords, self.sr = convert(self.filename1, self.canvas_height)
        self.first_sbar.set(0, 1 / (len(self.y_coords) / 1000))
        if self.srtfilename != "":
            self.mark_speech_segments()
        self.draw_waveform1()
        self.check_files()
        self.first.bind('<Enter>', self._bound_to_mousewheel)
        self.first.bind('<Leave>', self._unbound_to_mousewheel)
        self.toplevel_window.destroy()

    def chooseFile_btn2_event(self):
        previous2 = self.filename2

        if self.example_loaded == 1:
            self.filename2 = askopenfilename(filetypes=(('Mp4, WAV files', '*.mp4;*.wav'), ('All files', '*.*')),
                                             initialdir=os.getcwd(), title="Choose second Mp4 file")

        if self.filename2 == "":
            self.filename2 = previous2
            return
        elif self.filename2.rsplit(".", 1)[1] not in ("mp4", "wav"):
            showinfo("Wrong file type", f"File \"{self.filename2.rsplit('/', 1)[-1]}\" is not an Mp4 file!")
            return
        # self.switch_mode.set("WAV")
        # self.select_frame_by_name("WAV")
        # self.second_frame_label.configure(text=self.filename2.rsplit(".", 1)[0].rsplit("/", 1)[-1]+".wav")
        print(self.filename2)
        self.window_handler(self.generating_waveform2)

    def generating_waveform2(self):
        if self.filename2.rsplit(".", 1)[1] == "mp4":
            self.video2_setup()
        self.toplevel_window.focus()
        self.y_coords2, _ = convert(self.filename2, self.canvas_height)
        self.second_sbar.set(0, 1 / (len(self.y_coords2) / 1000))
        self.draw_waveform2()
        self.check_files()
        self.second.bind('<Enter>', self._bound_to_mousewheel)
        self.second.bind('<Leave>', self._unbound_to_mousewheel)
        self.toplevel_window.destroy()

    def choose_srtFile_event(self):
        previousSrt = self.srtfilename

        if self.example_loaded == 1:
            self.srtfilename = askopenfilename(filetypes=(('SRT files', '*.srt'), ('All files', '*.*')),
                                               initialdir=os.getcwd(), title="Choose SRT subtitle file")

        if self.srtfilename == "":
            self.srtfilename = previousSrt
            return
        elif self.srtfilename.rsplit(".", 1)[1] != "srt":
            showinfo("Wrong file type", f"File \"{self.srtfilename.rsplit('/', 1)[-1]}\" is not an SRT file!")
            return
        print(self.srtfilename)
        # tf = open(self.srtfilename, encoding="utf8")
        # orig_sub_txt = tf.read()
        self.orig_sub.configure(state="normal")
        self.orig_sub.delete("0.0", "end")
        self.insert_subs()

        self.orig_sub.tag_add("Title", "1.0", "1.20")
        self.orig_sub.tag_config("speech")
        self.orig_sub.tag_bind("speech", '<Button-1>', self.sub_click_event)
        self.orig_sub.configure(state="disabled")
        self.srt_add.place_forget()
        # self.switch_mode.set("SRT")
        # self.select_frame_by_name("SRT")
        if self.filename1 != "":
            self.mark_speech_segments()
        self.check_files()

    def insert_subs(self):
        self.orig_sub.insert("0.0", "Original subtitles:\n")
        subs = pysrt.open(self.srtfilename)
        index_len = len(str(len(subs)))
        self.orig_sub.insert("end", "\n")
        for sub in subs:
            if sub.index in (10, 100, 1000):
                index_len -= 1
            num_time_first = ' ' * index_len + '   '.join(str(sub).split('\n')[:3])
            sub_width = len(num_time_first) - len(sub.text.split("\n", 1)[0])
            other_lines = [' ' * sub_width + line for line in str(sub).splitlines()[3:]]
            processed_sub = num_time_first + '\n' + '\n'.join(other_lines)
            if processed_sub[-1] != "\n":
                processed_sub += "\n"
            processed_sub += "\n"
            self.orig_sub.insert("end", processed_sub, ("speech", str(sub.index - 1)))
            self.orig_sub.tag_bind(str(sub.index - 1), "<Enter>", self.on_enter_sub)
            self.orig_sub.tag_bind(str(sub.index - 1), "<Leave>", self.on_leave_sub)

    def on_enter_sub(self, event):
        index = self.orig_sub.index("@%s,%s" % (event.x, event.y))
        tags = self.orig_sub.tag_names(index)
        self.previous_tag1 = tags[1]
        if self.orig_sub.tag_cget(tags[1], "background") in ("#eab17f", "#925827"):
            return
        event.widget.tag_configure(tags[1], background="#dbdbdb")
        if self.appearance_mode_menu.get() == 1:
            event.widget.tag_configure(tags[1], background="#2b2b2b")

    def on_leave_sub(self, event):
        if self.orig_sub.tag_cget(self.previous_tag1, "background") in ("#eab17f", "#925827"):
            return
        event.widget.tag_configure(self.previous_tag1, background="")
        event.widget.tag_configure("speech", background="")

    def on_enter_Asub(self, event):
        index = self.aligned_sub.index("@%s,%s" % (event.x, event.y))
        tags = self.aligned_sub.tag_names(index)
        self.previous_tag1A = tags[1]
        if self.aligned_sub.tag_cget(tags[1], "background") in ("#eab17f", "#925827"):
            return
        event.widget.tag_configure(tags[1], background="#dbdbdb")
        if self.appearance_mode_menu.get() == 1:
            event.widget.tag_configure(tags[1], background="#2b2b2b")

    def on_leave_Asub(self, event):
        if self.aligned_sub.tag_cget(self.previous_tag1A, "background") in ("#eab17f", "#925827"):
            return
        event.widget.tag_configure(self.previous_tag1A, background="")
        event.widget.tag_configure("speech", background="")

    # https://stackoverflow.com/a/24145562
    def sub_click_event(self, event):
        index = self.orig_sub.index("@%s,%s" % (event.x, event.y))
        tags = self.orig_sub.tag_names(index)
        sub_index = tags[1]
        # if the text is highlighted by dragging the mouse, tag sel is added to tags = ("sel", "speech", "id"), we want sub_index = id
        if sub_index == "speech":
            sub_index = tags[2]

        # scroll to selected segment
        self.selected = sub_index
        x0, x1 = self.segments[int(sub_index)]
        img_width = x1 - x0
        # offset to make the selected segment appear in the middle of the canvas
        offset = (self.canvas_width - img_width) / 2
        scroll = (x0 - offset) / (len(self.y_coords) / 10)
        self.first_sbar.set(scroll, scroll)
        self.highlight_selected(sub_index)

    def sub_click_eventA(self, event):
        index = self.aligned_sub.index("@%s,%s" % (event.x, event.y))
        tags = self.aligned_sub.tag_names(index)
        sub_index = tags[1]
        # if the text is highlighted by dragging the mouse, tag sel is added to tags = ("sel", "speech", "id"), we want sub_index = id
        if sub_index == "speech":
            sub_index = tags[2]

        # scroll to selected segment
        self.selectedA = sub_index
        x0, x1 = self.segmentsA[int(sub_index)]
        img_width = x1 - x0
        # offset to make the selected segment appear in the middle of the canvas
        offset = (self.canvas_width - img_width) / 2
        scroll = (x0 - offset) / (len(self.y_coords2) / 10)
        self.second_sbar.set(scroll, scroll)
        self.highlight_selectedA(sub_index)

    def video1_setup(self):
        bg = self.cm["fr_bg_l"]
        fg = "black"
        if self.appearance_mode_menu.get() == 1:
            bg = self.cm["fr_bg_d"]
            fg = "white"
        self.play_button1.configure(state="normal")
        self.slider1.configure(state="normal")
        self.slider1.set(0)
        self.play_button1.configure(image=self.play_icon)
        self.addvid1.pack_forget()
        if self.video1 != "not_setup":
            self.video1.pack_forget()
        self.video1 = TkinterVideo(master=self.tkvideo1, fg=fg, background=bg, text="Click play to play video!",
                                   font=customtkinter.CTkFont(size=20), keep_aspect=True)
        self.video1.load(self.filename1)
        self.video1.pack(fill="both", expand=True, padx=4, pady=2)
        # self.video1.set_size((600, 450)) # sets the frame size
        self.video1.bind("<<Duration>>", self.update_duration1)
        self.video1.bind("<<SecondChanged>>", self.update_slider1)
        self.video1.bind("<<Ended>>", self.video_ended1)

    def video2_setup(self):
        bg = self.cm["fr_bg_l"]
        fg = "black"
        if self.appearance_mode_menu.get() == 1:
            bg = self.cm["fr_bg_d"]
            fg = "white"
        self.play_button2.configure(state="normal")
        self.slider2.configure(state="normal")
        self.slider2.set(0)
        self.play_button2.configure(image=self.play_icon)
        self.addvid2.pack_forget()
        if self.video2 != "not_setup":
            self.video2.pack_forget()
        self.video2 = TkinterVideo(master=self.tkvideo2, fg=fg, background=bg, text="Click play to play video!",
                                   font=customtkinter.CTkFont(size=20), keep_aspect=True)
        self.video2.load(self.filename2)
        self.video2.pack(fill="both", expand=True, padx=4, pady=2)
        # self.video1.set_size((600, 450)) # sets the frame size
        self.video2.bind("<<Duration>>", self.update_duration2)
        self.video2.bind("<<SecondChanged>>", self.update_slider2)
        self.video2.bind("<<Ended>>", self.video_ended2)

    def update_duration1(self, event):
        """ updates the duration after finding the duration """
        print("here1")
        duration = self.video1.video_info()["duration"]
        self.end_time1.configure(text=str(datetime.timedelta(seconds=duration)).rsplit(".")[0])
        self.slider1.configure(to=duration)
        print(duration)

    def update_duration2(self, event):
        """ updates the duration after finding the duration """
        print("here1")
        duration = self.video2.video_info()["duration"]
        self.end_time2.configure(text=str(datetime.timedelta(seconds=duration)).rsplit(".")[0])
        self.slider2.configure(to=duration)
        print(duration)

    def seek1(self, val):
        print("seeked to:", int(val))
        self.video1.seek(math.ceil(val))
        if self.video1.is_paused():
            self.video1.play()
            self.video1.pause()

    def seek2(self, val):
        print("seeked to:", int(val))
        self.video2.seek(math.ceil(val))
        if self.video2.is_paused():
            self.video2.play()
            self.video2.pause()

    def play_pause1(self):
        if self.video1.is_paused():
            print("paused")
            self.video1.play()
            self.play_button1.configure(image=self.pause_icon)
            return
        print("not paused")
        self.video1.pause()
        self.play_button1.configure(image=self.play_icon)

    def play_pause2(self):
        if self.video2.is_paused():
            print("paused")
            self.video2.play()
            self.play_button2.configure(image=self.pause_icon)
            return
        print("not paused")
        self.video2.pause()
        self.play_button2.configure(image=self.play_icon)

    def update_slider1(self, event):
        dur = self.video1.current_duration()
        self.slider1.set(dur)
        self.end_time1.configure(text=str(datetime.timedelta(seconds=dur)).rsplit(".")[0])

    def update_slider2(self, event):
        dur = self.video2.current_duration()
        self.slider2.set(dur)
        self.end_time2.configure(text=str(datetime.timedelta(seconds=dur)).rsplit(".")[0])

    def video_ended1(self, event):
        self.slider1.set(0)
        self.play_button1.configure(image=self.play_icon)

    def video_ended2(self, event):
        self.slider2.set(0)
        self.play_button2.configure(image=self.play_icon)

    def draw_waveform1(self, *args):
        if self.filename1 == "":
            return
        self.first.delete("all")
        l1, _ = self.first_sbar.get()
        d1 = int(len(self.y_coords) * l1)
        d2 = d1 + self.canvas_width * 10
        self.first.create_line(*zip(self.x_coords, (self.canvas_height / 2 - self.y_coords[d1:d2])),
                               fill=self.normal_fill)
        # if len(self.signal_mismatch) != 0:
        #     rem = self.signal_mismatch - d1/10
        #     # Set any negative values in the first column to 0
        #     rem[:, 0] = np.maximum(rem[:, 0], 0)
        #     # Identify the indices of any subarrays where the first element is greater than 10000 or the second element is negative
        #     indices_to_remove = np.logical_or(rem[:, 0] > 1000, rem[:, 1] < 0)
        #     # Remove those subarrays from x
        #     rem = rem[~indices_to_remove]
        #     for r in rem:
        #         x = np.arange(r[0], r[1], 0.1)
        #         self.first.create_line(*zip(x, (self.canvas_height / 2 - self.y_coords[int(d1+r[0]*10):int(d1+r[1]*10)])), fill=self.removed_fill)
        if self.srtfilename == "":
            return
        self.create_speech_rectangles(d1 / 10, d2 / 10)

    def mark_speech_segments(self):
        segments = get_speech_segments(self.srtfilename)
        self.segments = segments * (self.sr / 10)
        self.images = []
        for seg in self.segments:
            self.prepare_images(seg[0], 0, seg[1], self.canvas_height, fill="#ff4f19", alpha=.5)
        self.create_speech_rectangles(0, self.canvas_width)
        # self.create_rectangle(seg[0], 0, seg[1], self.canvas_height, fill="#ff4f19", alpha=.5, outline="orange", tags=("speech", str(id)))
        self.first.tag_bind("speech", "<Button-1>", self.selected_speech_event)
        print("SIZE OF IMAGES", sys.getsizeof(self.images))

    def selected_speech_event(self, event):
        item = event.widget.find_withtag('current')
        tags = self.first.itemcget(item, "tags")
        id = tags.split(" ")[1]

        self.selected = id

        # scroll to deleted
        try:
            print("id", int(id) + 1)
            print(self.grouped)
            index = np.where([int(id) + 1 in subarr for subarr in self.grouped])[0]
            print("index", self.signal_mismatch[index])
            offset = self.canvas_width / 2 * 10
            scroll = (self.signal_mismatch[index] - offset) / len(self.y_coords2)
            print("scroll", scroll)
            self.second_sbar.set(scroll, scroll)
            self.draw_waveform2()
        except:
            pass

        self.highlight_selected(id)

        # scroll to subs
        self.orig_sub.see(id + ".first")
        line = self.orig_sub.dlineinfo(id + ".first")
        better_offset = 10  # for better visual
        self.orig_sub.yview_scroll(line[1] - better_offset, 'pixels')

    def highlight_selected(self, id):
        print("highlighting" + id)

        self.draw_waveform1()

        # seek in video
        x0, _ = self.segments[int(id)]
        if self.video1 != "not_setup":
            self.seek1(x0 * 10 / self.sr)

        # erase previous subtitle highlting
        if self.previous_tag2 is not None:
            self.orig_sub.tag_config(self.previous_tag2, background="")
        self.previous_tag2 = id
        # and create new sub highliting
        self.orig_sub.tag_config(id, background="#eab17f")
        if self.appearance_mode_menu.get() == 1:
            self.orig_sub.tag_config(id, background="#925827")

    def draw_waveform2(self, *args):
        if self.filename2 == "":
            return
        self.second.delete("all")
        l1, _ = self.second_sbar.get()
        d1 = int(len(self.y_coords2) * l1)
        d2 = d1 + self.canvas_width * 10
        indices = np.where((d2 >= self.signal_mismatch) & (d1 <= self.signal_mismatch))[0]
        for i in indices:
            x = (self.signal_mismatch[i] - d1) / 10
            self.second.create_rectangle(x, 0, x + 5, self.canvas_height, fill=self.removed_fill,
                                         outline=self.removed_fill, tags=("removed", str(i)))
        self.second.create_line(*zip(self.x_coords, (self.canvas_height / 2 - self.y_coords2[d1:d2])),
                                fill=self.normal_fill)
        if self.fname == "":
            return
        self.create_speech_rectanglesA(d1 / 10, d2 / 10)

    def mark_speech_segmentsA(self):
        segments = get_speech_segments(self.fname)
        self.segmentsA = segments * (self.sr / 10)
        self.imagesA = []
        for seg in self.segmentsA:
            self.prepare_imagesA(seg[0], 0, seg[1], self.canvas_height, fill="#ff4f19", alpha=.5)
        self.create_speech_rectanglesA(0, self.canvas_width)
        # self.create_rectangle(seg[0], 0, seg[1], self.canvas_height, fill="#ff4f19", alpha=.5, outline="orange", tags=("speech", str(id)))
        self.second.tag_bind("speech", "<Button-1>", self.selected_speech_eventA)
        self.second.tag_bind("removed", "<Button-1>", self.selected_speech_eventA)
        print("SIZE OF IMAGES", sys.getsizeof(self.images))

    def selected_speech_eventA(self, event):
        item = event.widget.find_withtag('current')
        tags = self.second.itemcget(item, "tags")
        id = tags.split(" ")[1]

        self.selectedA = id
        print(tags)
        # if a deleted segment is selected (the scene missing from the second video)
        # scroll to segment in first waveform
        if tags.split(" ")[0] == "removed":
            # get the first deleted subtitle
            id_del = self.grouped[int(id)][0]
            print(id_del)
            x0, x1 = self.segments[int(id_del) - 1]
            img_width = x1 - x0
            # offset to make the selected segment appear in the middle of the canvas
            offset = (self.canvas_width - img_width) / 2
            scroll = (x0 - offset) / (len(self.y_coords) / 10)
            self.first_sbar.set(scroll, scroll)
            self.draw_waveform1()
            return

        self.highlight_selectedA(id)

        # scroll to subs
        self.aligned_sub.see(id + ".first")
        line = self.aligned_sub.dlineinfo(id + ".first")
        better_offset = 10  # for better visual
        self.aligned_sub.yview_scroll(line[1] - better_offset, 'pixels')

    def highlight_selectedA(self, id):
        print("highlighting" + id)

        self.draw_waveform2()

        # seek in video
        x0, _ = self.segmentsA[int(id)]
        if self.video2 != "not_setup":
            self.seek2(x0 * 10 / self.sr)

        # erase previous subtitle highlting
        if self.previous_tag2A is not None:
            self.aligned_sub.tag_config(self.previous_tag2A, background="")
        self.previous_tag2A = id
        # and create new sub highliting
        self.aligned_sub.tag_config(id, background="#eab17f")
        if self.appearance_mode_menu.get() == 1:
            self.aligned_sub.tag_config(id, background="#925827")

    def align_event(self):
        # create a new window
        self.toplevel_window = ToplevelWindow(self.appearance_mode_menu.get())
        self.toplevel_window.label.configure(text="Aligning signals...")
        # start a new thread to run the event handling code
        t = threading.Thread(target=self.align_signals)
        t.daemon = True
        t.start()

        # wait for the window to be destroyed before continuing
        self.toplevel_window.wait_window()

    def align_signals(self):
        self.toplevel_window.focus()
        filenames = [self.filename1, self.filename2, self.srtfilename]
        self.removed_indexes, self.signal_mismatch, self.grouped = align(filenames)
        # self.removed_indexes, self.signal_mismatch, self.grouped = align_test()
        self.signal_mismatch = np.array(self.signal_mismatch)
        self.signal_mismatch = self.signal_mismatch * self.sr
        # print("Aligned", self.removed_indexes, self.signal_mismatch)
        self.aligned_text.configure(text="Subtiles Aligned!")
        # showinfo("Dialog", "Subtitles Aligned!")
        self.align_button.configure(state="disabled")
        self.out_srt()
        self.aligned_sub.tag_config("speech")
        self.aligned_sub.tag_bind("speech", '<Button-1>', self.sub_click_eventA)
        self.mark_speech_segmentsA()
        self.out_wav()
        # close the window
        self.toplevel_window.destroy()

    def out_srt(self):
        self.aligned_sub.configure(state="normal")
        self.aligned_sub.delete("0.0", "end")
        self.not_aligned_label.place_forget()
        self.fname = self.filename2.rsplit(".", 1)[0] + ".srt"
        self.aligned_sub.insert("0.0", "Aligned subtitles:\n")
        subs = pysrt.open(self.fname)
        # reindexes the subs in the right order
        subs.clean_indexes()
        index_len = len(str(len(subs)))
        self.aligned_sub.insert("end", "\n")
        for sub in subs:
            if sub.index in (10, 100, 1000):
                index_len -= 1
            num_time_first = ' ' * index_len + '   '.join(str(sub).split('\n')[:3])
            sub_width = len(num_time_first) - len(sub.text.split("\n", 1)[0])
            other_lines = [' ' * sub_width + line for line in str(sub).splitlines()[3:]]
            processed_sub = num_time_first + '\n' + '\n'.join(other_lines)
            if processed_sub[-1] != "\n":
                processed_sub += "\n"
            processed_sub += "\n"
            self.aligned_sub.insert("end", processed_sub, ("speech", str(sub.index - 1)))
            self.aligned_sub.tag_bind(str(sub.index - 1), "<Enter>", self.on_enter_Asub)
            self.aligned_sub.tag_bind(str(sub.index - 1), "<Leave>", self.on_leave_Asub)
        self.aligned_sub.configure(state="disabled")

        self.orig_sub.configure(state="normal")
        for id in self.removed_indexes:
            self.orig_sub.tag_config(str(id - 1), foreground=self.removed_fill, overstrike=True)
        self.orig_sub.configure(state="disabled")

    def out_wav(self):
        if len(self.signal_mismatch) == 0:
            return
        self.prepare_removed_images()
        self.draw_waveform1()
        self.draw_waveform2()

    def prepare_removed_images(self):
        for id in self.removed_indexes:
            w = self.images[id - 1].width()
            h = self.images[id - 1].height()
            red_color = (219, 55, 55, 127)
            image = Image.new('RGBA', (w, h), red_color)
            self.images[id - 1] = ImageTk.PhotoImage(image)

    # https://stackoverflow.com/a/54645103
    def prepare_images(self, x1, y1, x2, y2, **kwargs):
        alpha = int(kwargs.pop('alpha') * 255)
        fill = kwargs.pop('fill')
        orange_color = (250, 135, 35)
        fill = orange_color + (alpha,)
        image = Image.new('RGBA', (int(x2 - x1) + 1, int(y2 - y1) + 1), fill)
        self.images.append(ImageTk.PhotoImage(image))

    def create_speech_rectangles(self, d1, d2):
        indices = np.where((d2 >= self.segments[:, 0]) & (d1 <= self.segments[:, 1]))[0]
        y0 = 0
        y1 = self.canvas_height
        for id in indices:
            outline = "orange"
            if id + 1 in self.removed_indexes:
                outline = "red"
            x = self.segments[id] - d1
            tags = ("speech", str(id))
            self.first.create_image(x[0], y0, image=self.images[id], anchor='nw', tags=tags)
            self.first.create_text(x[0] + (x[1] - x[0]) / 2, y1 / 2, text=str(int(tags[1]) + 1), tags=tags,
                                   fill="white",
                                   font=customtkinter.CTkFont(size=25, weight="bold"))
            self.first.create_rectangle(x[0], y0, x[1], y1, outline=outline, tags=tags)
            if str(id) == self.selected:
                self.first.create_image(x[0], y0, image=self.images[id], anchor='nw', tags=tags)
                self.first.create_text(x[0] + (x[1] - x[0]) / 2, y1 / 2, text=str(int(tags[1]) + 1), tags=tags,
                                       fill="white",
                                       font=customtkinter.CTkFont(size=25, weight="bold"))
                self.first.create_rectangle(x[0], y0, x[1], y1, outline=outline, tags=tags)

    def prepare_imagesA(self, x1, y1, x2, y2, **kwargs):
        alpha = int(kwargs.pop('alpha') * 255)
        fill = kwargs.pop('fill')
        orange_color = (250, 135, 35)
        fill = orange_color + (alpha,)
        image = Image.new('RGBA', (int(x2 - x1) + 1, int(y2 - y1) + 1), fill)
        self.imagesA.append(ImageTk.PhotoImage(image))

    def create_speech_rectanglesA(self, d1, d2):
        indices = np.where((d2 >= self.segmentsA[:, 0]) & (d1 <= self.segmentsA[:, 1]))[0]
        # x_coords = self.segments[indices[0]:indices[-1]+1] - d1
        # images = self.images[indices[0]:indices[-1]+1]
        y0 = 0
        y1 = self.canvas_height
        for id in indices:
            x = self.segmentsA[id] - d1
            tags = ("speech", str(id))
            self.second.create_image(x[0], y0, image=self.imagesA[id], anchor='nw', tags=tags)
            self.second.create_text(x[0] + (x[1] - x[0]) / 2, y1 / 2, text=str(int(tags[1]) + 1), tags=tags,
                                    fill="white",
                                    font=customtkinter.CTkFont(size=25, weight="bold"))
            self.second.create_rectangle(x[0], y0, x[1], y1, outline="orange", tags=tags)
            if str(id) == self.selectedA:
                self.second.create_image(x[0], y0, image=self.imagesA[id], anchor='nw', tags=tags)
                self.second.create_text(x[0] + (x[1] - x[0]) / 2, y1 / 2, text=str(int(tags[1]) + 1), tags=tags,
                                        fill="white",
                                        font=customtkinter.CTkFont(size=25, weight="bold"))
                self.second.create_rectangle(x[0], y0, x[1], y1, outline="orange", tags=tags)

    def check_files(self):
        if self.srtfilename != "" and self.filename1 != "" and self.filename2 != "":
            self.align_button.configure(state="normal")
            # self.align_button2.configure(state="normal")

    def clear_window(self):

        if self.example_loaded == 0:
            self.chooseFile_btn1_event()
            self.chooseFile_btn2_event()
            self.choose_srtFile_event()
            self.example_loaded = 1
            return

        self.filename1 = ""
        self.filename2 = ""
        self.srtfilename = ""

        self.aligned_text.configure(text="")
        self.init_mainWindow()
        self.change_appearance_mode_event()

    def change_appearance_mode_event(self):
        if self.appearance_mode_menu.get() == 1:
            customtkinter.set_appearance_mode("dark")
            self.first.configure(background="#2b2b2b", highlightbackground="#2b2b2b")
            self.second.configure(background="#2b2b2b", highlightbackground="#2b2b2b")
            try:
                self.orig_sub.tag_config(self.previous_tag2, background="#925827")
                self.aligned_sub.tag_config(self.previous_tag2A, background="#925827")
            except:
                print("subs not yet loaded")
            try:
                self.video1.configure(background=self.cm["fr_bg_d"], fg="white")
                self.video2.configure(background=self.cm["fr_bg_d"], fg="white")
            finally:
                return
        customtkinter.set_appearance_mode("light")
        self.first.configure(background="#dbdbdb", highlightbackground="#dbdbdb")
        self.second.configure(background="#dbdbdb", highlightbackground="#dbdbdb")
        try:
            self.orig_sub.tag_config(self.previous_tag2, background="#eab17f")
            self.aligned_sub.tag_config(self.previous_tag2A, background="#eab17f")
        except:
            print("subs not yet loaded")
        try:
            self.video1.configure(background=self.cm["fr_bg_l"], fg="black")
            self.video2.configure(background=self.cm["fr_bg_l"], fg="black")
        finally:
            return


if __name__ == "__main__":
    app = App()
    app.mainloop()
    # kill all daemon threads if align goes wrong
    sys.exit()
