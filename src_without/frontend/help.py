import customtkinter
import numpy as np
from tkinter.messagebox import showinfo
import tkinter as tk
from tkinter.filedialog import askopenfilename
import os
from misc.get_wav import get_wav
from backend.align import align
import sys
from PIL import Image, ImageTk
import threading
from frontend.components.toplevel import ToplevelWindow
from frontend.components.videoplayer import VideoPlayer
from frontend.components.subtitles import SubClass
from frontend.components.waveform import Waveform

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
        self.srtfilename2 = fname

        self.example_loaded = 1

        self.removed_fill = "#db3737"  # red
        self.normal_fill = "#2cbe79"  # green

        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..\icons")
        print(image_path)
        self.mp4_icon = customtkinter.CTkImage(light_image=Image.open("../icons/mp4add_ico_dark.png"),
                                               dark_image=Image.open("../icons/mp4add_ico_light.png"),
                                               size=(65, 65))
        self.srt_icon = customtkinter.CTkImage(light_image=Image.open("../icons/srtadd_ico_dark.png"),
                                               dark_image=Image.open("../icons/srtadd_ico_light.png"),
                                               size=(65, 65))
        self.add_icon = customtkinter.CTkImage(light_image=Image.open("../icons/add_dark.png"),
                                               dark_image=Image.open("../icons/add_light.png"),
                                               size=(50, 50))
        self.play_icon = customtkinter.CTkImage(light_image=Image.open("../icons/play_button.png"),
                                                size=(20, 20))
        self.pause_icon = customtkinter.CTkImage(light_image=Image.open("../icons/pause_button.png"),
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
        "Initiates all the components and variables into the main window"
        self.canvas_height = 250
        self.canvas_width = 915
        self.signal_mismatch = np.array([])
        self.removed_indexes = []
        self.x_coords = np.arange(0, self.canvas_width, 0.1)
        self.offset = 0

        # init videos
        self.tkvideo1 = VideoPlayer(self.main_frame, mas=self.main_frame, rw=1, fg_color=("#dbdbdb", "#2b2b2b"), corner_radius=10, width=140)
        self.tkvideo1.grid(row=0, column=0, sticky="nsew", pady=(10, 0), padx=(10, 0))
        self.tkvideo1.addvid.configure(command=self.chooseFile_btn1_event)
        
        self.tkvideo2 = VideoPlayer(self.main_frame, mas=self.main_frame, rw=3, fg_color=("#dbdbdb", "#2b2b2b"), corner_radius=10, width=140)
        self.tkvideo2.grid(row=2, column=0, sticky="nsew", pady=(5, 0), padx=(10, 0))
        self.tkvideo2.addvid.configure(command=self.chooseFile_btn2_event)
        
        # setup canvases for waveforms
        self.first_frame = Waveform(master=self.main_frame, mode="in", other_frame=None, video=self.tkvideo1, srt_fname=self.srtfilename, fname=self.filename1,
                                     fg_color=("#dbdbdb", "#2b2b2b"),
                                     corner_radius=10)
        self.first_frame.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="nsew")
        self.update()
        self.first_frame.canvas.create_line(0, self.first_frame.canvas.winfo_height() / 2, self.canvas_width,
                                            self.first_frame.canvas.winfo_height() / 2, fill=self.normal_fill)
        self.first_frame.scrollbar.configure(command=self.first_frame.draw_waveform)

        self.second_frame = Waveform(master=self.main_frame, mode="out", other_frame=self.first_frame, video=self.tkvideo2, srt_fname=self.srtfilename2, fname=self.filename2,
                                      fg_color=("#dbdbdb", "#2b2b2b"), 
                                      corner_radius=10)
        self.second_frame.grid(row=2, column=1, padx=10, pady=(5, 0), sticky="nsew")
        self.update()
        self.second_frame.canvas.create_line(0, self.second_frame.canvas.winfo_height() / 2, self.canvas_width,
                                             self.second_frame.canvas.winfo_height() / 2, fill=self.normal_fill)
        self.second_frame.scrollbar.configure(command=self.second_frame.draw_waveform)
        self.first_frame.other_frame = self.second_frame
        
        # initiate subs frame
        self.orig_sub = SubClass(self.subs_frame, mode="in", frame=self.first_frame, appr=self.appearance_mode_menu.get(), corner_radius=10,
                                                    text_color=("gray10", "gray90"),
                                                    height=260, wrap="none",
                                                    font=customtkinter.CTkFont(family="Consolas"))
        self.first_frame.sub = self.orig_sub
        self.orig_sub.grid(row=0, column=0, padx=10, pady=0, sticky="we")
        self.orig_sub.srt_add.configure(fg_color="transparent", image=self.add_icon, command=self.choose_srtFile_event)

        self.aligned_sub = SubClass(self.subs_frame, mode="out", frame=self.second_frame, appr=self.appearance_mode_menu.get(), corner_radius=10,
                                                    text_color=("gray10", "gray90"),
                                                    height=260, wrap="none",
                                                    font=customtkinter.CTkFont(family="Consolas"))
        self.aligned_sub.grid(row=0, column=1, padx=10, pady=0, sticky="ew")
        self.second_frame.sub = self.aligned_sub

        self.align_button.configure(state="disabled")

    def _bound_to_mousewheel(self, event):
        """Binds the _on_mousewheel function to the <MouseWheel> scrolling event."""
        self.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        """Unbinds the _on_mousewheel function from the <MouseWheel> scrolling event."""
        self.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """Scrolls the waveform canvas in response to mousewheel scroll.
        Determines which canvas widget was scrolled, then adjusts the scrollbar and redraws the waveform.
        """
        if event.widget.winfo_id() == self.first_frame.canvas.winfo_id():
            widget = self.first_frame.scrollbar
            func = self.first_frame.draw_waveform
        elif event.widget.winfo_id() == self.second_frame.canvas.winfo_id():
            widget = self.second_frame.scrollbar
            func = self.second_frame.draw_waveform
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
        """Displays a toplevel window and runs a function in a separate thread.
        The function is started in a new thread and the window is destroyed after the function completes.
        """
        self.toplevel_window = ToplevelWindow(mode=self.appearance_mode_menu.get())
        self.toplevel_window.focus()
        # start a new thread to run the event handling code
        t = threading.Thread(target=func)
        t.daemon = True
        t.start()
        
        # wait for the window to be destroyed before continuing
        self.toplevel_window.wait_window()

    def chooseFile_btn1_event(self):
        """Displays a file dialog to choose an audio or video file.
        If a file is selected, the generating_waveform1 function is called to generate the first waveform from the file.
        """
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
        self.first_frame.fname = self.filename1
        self.window_handler(self.generating_waveform1)

    def generating_waveform1(self):
        """Generates the waveform for the first audio or video file.
        Converts the audio or video file to a waveform and displays it onto the first canvas.
        """
        if self.filename1.rsplit(".", 1)[1] == "mp4":
            self.tkvideo1.video_setup(self.appearance_mode_menu.get(), self.filename1)
        self.toplevel_window.focus()
        self.first_frame.y_coords, self.sr = get_wav(self.filename1, self.canvas_height)
        self.first_frame.sr = self.sr
        self.first_frame.x_coords = self.x_coords
        self.first_frame.gen_wav()
        if self.srtfilename != "":
            self.first_frame.mark_speech_segments()
        self.first_frame.canvas.bind('<Enter>', self._bound_to_mousewheel)
        self.first_frame.canvas.bind('<Leave>', self._unbound_to_mousewheel)
        self.check_files()
        self.toplevel_window.destroy()

    def chooseFile_btn2_event(self):
        """Displays a file dialog to choose a second audio or video file.
        If a file is selected, the generating_waveform2 function is called to generate the second waveform from the file.
        """
        previous2 = self.filename2

        if self.example_loaded == 1:
            self.filename2 = askopenfilename(filetypes=(('Mp4, WAV files', '*.mp4;*.wav'), ('All files', '*.*')),
                                             initialdir=os.getcwd(), title="Choose second Mp4 file")

        if self.filename2 == "":
            self.filename2 = previous2
            return
        elif self.filename2.rsplit(".", 1)[1] not in ("mp4", "wav"):
            showinfo("Wrong file type", f"File \"{self.filename2.rsplit('/', 1)[-1]}\" is not an Mp4/WAV file!")
            return
       
        print(self.filename2)
        self.second_frame.fname = self.filename2
        self.window_handler(self.generating_waveform2)

    def generating_waveform2(self):
        """Generates the waveform for the first audio or video file.
        Converts the audio or video file to a waveform and displays it onto the second canvas.
        """
        if self.filename2.rsplit(".", 1)[1] == "mp4":
            self.tkvideo2.video_setup(self.appearance_mode_menu.get(), self.filename2)
        self.toplevel_window.focus()
        self.second_frame.y_coords, _ = get_wav(self.filename2, self.canvas_height)
        self.second_frame.sr = self.sr
        self.second_frame.x_coords = self.x_coords
        self.second_frame.gen_wav()
        self.second_frame.canvas.bind('<Enter>', self._bound_to_mousewheel)
        self.second_frame.canvas.bind('<Leave>', self._unbound_to_mousewheel)
        self.check_files()
        self.toplevel_window.destroy()

    def choose_srtFile_event(self):
        """Displays a file dialog to choose an SRT subtitle file.
        If a file is selected, the in_srt function is called to process the file.
        """
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
        self.first_frame.srt_fname = self.srtfilename
        self.in_srt()
        
        if self.filename1 != "":
            self.first_frame.mark_speech_segments()
        self.check_files()

    def in_srt(self):
        """Inserts subtitles from an SRT file and bind the speech segments in the subtitle to the 
        sub_click_event function.
        """
        self.orig_sub.srt_add.place_forget()
        self.orig_sub.insert_subs(self.srtfilename)
        self.orig_sub.tag_bind("speech", '<Button-1>', self.orig_sub.sub_click_event)
        self.orig_sub.configure(state="disabled")

    def align_event(self):
        """
        Initiates the alignment of the two waveforms.
        """
        # create a new window
        self.toplevel_window = ToplevelWindow(self.appearance_mode_menu.get())
        self.toplevel_window.title("Aligning signals")
        self.toplevel_window.label.configure(text="Aligning signals...")
        self.toplevel_window.focus()
        # start a new thread to run the event handling code
        t = threading.Thread(target=self.align_signals)
        t.daemon = True
        t.start()

        # wait for the window to be destroyed before continuing
        self.toplevel_window.wait_window()

    def align_signals(self):
        """
        Aligns the two waveforms and creates a new SRT file with aligned subtitles.
        """
        self.toplevel_window.grab_set()
        filenames = [self.filename1, self.filename2, self.srtfilename]
        self.signal_mismatch, self.removed_indexes, self.first_frame.grouped = align(filenames)
        self.first_frame.removed_indexes = self.removed_indexes
        # self.removed_indexes, self.signal_mismatch, self.grouped = align_test()
        self.second_frame.signal_mismatch = np.array(self.signal_mismatch) * self.sr
        self.aligned_text.configure(text="Subtiles Aligned!")
        self.align_button.configure(state="disabled")
        self.out_srt()
        self.second_frame.mark_speech_segments()
        self.out_wav()
        # close the window
        self.toplevel_window.destroy()

    def out_srt(self):
        """
        Outputs the aligned SRT file and inserts into the aligned_sub textbox.
        """
        # remove not aligned label
        self.aligned_sub.not_aligned_label.place_forget()
        self.srtfilename2 = self.filename2.rsplit(".", 1)[0] + ".srt"
        self.second_frame.srt_fname = self.srtfilename2
        # insert subs
        self.aligned_sub.insert_subs(self.srtfilename2)
        self.aligned_sub.tag_bind("speech", '<Button-1>', self.aligned_sub.sub_click_event)
        self.aligned_sub.configure(state="disabled")

        # removed subs are red in original sub text
        self.orig_sub.configure(state="normal")
        for id in self.removed_indexes:
            self.orig_sub.tag_config(str(id - 1), foreground=self.removed_fill)
        self.orig_sub.configure(state="disabled")

    def out_wav(self):
        """
        Helper function that prepares the removed images and redraws the waveforms.
        """
        self.prepare_removed_images()
        self.first_frame.draw_waveform()
        self.second_frame.draw_waveform()

    def prepare_removed_images(self):
        """
        Prepares removed images by replacing them with red images of the same size.
        """
        for id in self.removed_indexes:
            print("here")
            w = self.first_frame.images[id - 1].width()
            h = self.first_frame.images[id - 1].height()
            red_color = (219, 55, 55, 127)
            image = Image.new('RGBA', (w, h), red_color)
            self.first_frame.images[id - 1] = ImageTk.PhotoImage(image)

    def check_files(self):
        """
        Checks if all required files have been selected.
        """
        if self.srtfilename != "" and self.filename1 != "" and self.filename2 != "":
            self.align_button.configure(state="normal")

    def clear_window(self):
        """
        Clears the window and resets all variables to their initial states.
        """
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

    def change_appr_of_widgets(self, appr):
        """
        Changes the appearance mode of the widgets based on the selected appearance mode.
        """
        bgc = "#dbdbdb"
        bgsub = "#eab17f"
        fg = "black"

        if appr == 1:
            bgc = "#2b2b2b"
            bgsub = "#925827"
            fg = "white"

        self.first_frame.canvas.configure(background=bgc, highlightbackground=bgc)
        self.second_frame.canvas.configure(background=bgc, highlightbackground=bgc)
       
        try:
            self.orig_sub.tag_config(self.orig_sub.previous_tag2, background=bgsub)
            self.aligned_sub.tag_config(self.aligned_sub.previous_tag2, background=bgsub)
        except:
            print("subs not yet loaded")
        try:
            self.tkvideo1.video.configure(background=bgc, fg=fg)
            self.tkvideo2.video.configure(background=bgc, fg=fg)
        finally:
            print("video not yet loaded")
            return

    def change_appearance_mode_event(self):
        """
        Changes the appearance mode of the window based on the selected mode in the theme switch.
        """
        if self.appearance_mode_menu.get() == 1:
            customtkinter.set_appearance_mode("dark")
            self.change_appr_of_widgets(1)
            self.orig_sub.appr = 1
            self.aligned_sub.appr = 1
            return
        customtkinter.set_appearance_mode("light")
        self.change_appr_of_widgets(0)
        self.orig_sub.appr = 0
        self.aligned_sub.appr = 0


if __name__ == "__main__":
    app = App()
    app.mainloop()
    # kill all daemon threads if align goes wrong
    sys.exit()
