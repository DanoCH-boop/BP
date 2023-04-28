import customtkinter
import numpy as np
from tkinter.messagebox import showinfo
import tkinter as tk
from tkinter.filedialog import askopenfilename
import os
from misc.convert import convert
from backend.align import align
from misc.speech_segments import get_speech_segments
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
        self.fname = fname

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
        self.y_coords = []
        self.y_coords2 = []
        self.offset = 0

        # init videos
        self.tkvideo1 = VideoPlayer(self.main_frame, mas=self.main_frame, rw=1, fg_color=("#dbdbdb", "#2b2b2b"), corner_radius=10, width=140)
        self.tkvideo1.grid(row=0, column=0, sticky="nsew", pady=(10, 0), padx=(10, 0))
        self.tkvideo1.addvid.configure(command=self.chooseFile_btn1_event)
        
        self.tkvideo2 = VideoPlayer(self.main_frame, mas=self.main_frame, rw=3, fg_color=("#dbdbdb", "#2b2b2b"), corner_radius=10, width=140)
        self.tkvideo2.grid(row=2, column=0, sticky="nsew", pady=(5, 0), padx=(10, 0))
        self.tkvideo2.addvid.configure(command=self.chooseFile_btn2_event)
        
        # setup canvases for waveforms
        self.first_frame = Waveform(master=self.main_frame, fg_color=("#dbdbdb", "#2b2b2b"), corner_radius=10)
        self.first_frame.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="nsew")
        self.update()
        self.first_frame.canvas.create_line(0, self.first_frame.canvas.winfo_height() / 2, self.canvas_width,
                                            self.first_frame.canvas.winfo_height() / 2, fill=self.normal_fill)
        self.first_frame.scrollbar.configure(command=self.draw_waveform1)

        self.second_frame = Waveform(master=self.main_frame, fg_color=("#dbdbdb", "#2b2b2b"), corner_radius=10)
        self.second_frame.grid(row=2, column=1, padx=10, pady=(5, 0), sticky="nsew")
        self.update()
        self.second_frame.canvas.create_line(0, self.second_frame.canvas.winfo_height() / 2, self.canvas_width,
                                             self.second_frame.canvas.winfo_height() / 2, fill=self.normal_fill)
        self.second_frame.scrollbar.configure(command=self.draw_waveform2)
        
    
        # initiate subs frame
        self.orig_sub = SubClass(self.subs_frame, mode="in", appr=self.appearance_mode_menu.get(), corner_radius=10,
                                                    text_color=("gray10", "gray90"),
                                                    height=260, wrap="none",
                                                    font=customtkinter.CTkFont(family="Consolas"))
        self.orig_sub.grid(row=0, column=0, padx=10, pady=0, sticky="we")
        self.orig_sub.srt_add.configure(fg_color="transparent", image=self.add_icon, command=self.choose_srtFile_event)

        self.aligned_sub = SubClass(self.subs_frame, mode="out", appr=self.appearance_mode_menu.get(), corner_radius=10,
                                                    text_color=("gray10", "gray90"),
                                                    height=260, wrap="none",
                                                    font=customtkinter.CTkFont(family="Consolas"))
        self.aligned_sub.grid(row=0, column=1, padx=10, pady=0, sticky="ew")

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
            func = self.draw_waveform1
        elif event.widget.winfo_id() == self.second_frame.canvas.winfo_id():
            widget = self.second_frame.scrollbar
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
        self.window_handler(self.generating_waveform1)

    def generating_waveform1(self):
        """Generates the waveform for the first audio or video file.
        Converts the audio or video file to a waveform and displays it onto the first canvas.
        """
        if self.filename1.rsplit(".", 1)[1] == "mp4":
            self.tkvideo1.video_setup(self.appearance_mode_menu.get(), self.filename1)
        self.toplevel_window.focus()
        self.y_coords, self.sr = convert(self.filename1, self.canvas_height)
        self.first_frame.scrollbar.set(0, 1 / (len(self.y_coords) / 1000))
        if self.srtfilename != "":
            self.mark_speech_segments()
        self.draw_waveform1()
        self.check_files()
        self.first_frame.canvas.bind('<Enter>', self._bound_to_mousewheel)
        self.first_frame.canvas.bind('<Leave>', self._unbound_to_mousewheel)
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
            showinfo("Wrong file type", f"File \"{self.filename2.rsplit('/', 1)[-1]}\" is not an Mp4 file!")
            return
       
        print(self.filename2)
        self.window_handler(self.generating_waveform2)

    def generating_waveform2(self):
        """Generates the waveform for the first audio or video file.
        Converts the audio or video file to a waveform and displays it onto the second canvas.
        """
        if self.filename2.rsplit(".", 1)[1] == "mp4":
            self.tkvideo2.video_setup(self.appearance_mode_menu.get(), self.filename2)
        self.toplevel_window.focus()
        self.y_coords2, _ = convert(self.filename2, self.canvas_height)
        self.second_frame.scrollbar.set(0, 1 / (len(self.y_coords2) / 1000))
        self.draw_waveform2()
        self.check_files()
        self.second_frame.canvas.bind('<Enter>', self._bound_to_mousewheel)
        self.second_frame.canvas.bind('<Leave>', self._unbound_to_mousewheel)
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

        self.in_srt()
        
        if self.filename1 != "":
            self.mark_speech_segments()
        self.check_files()

    def in_srt(self):
        """Inserts subtitles from an SRT file and bind the speech segments in the subtitle to the 
        sub_click_event function.
        """
        self.orig_sub.srt_add.place_forget()
        self.orig_sub.insert_subs(self.srtfilename)
        self.orig_sub.tag_bind("speech", '<Button-1>', self.sub_click_event)
        self.orig_sub.configure(state="disabled")

    # https://stackoverflow.com/a/24145562
    def sub_click_event(self, event):
        """Handles the click event on a speech segment in the first subtitles and highlights the corresponding 
        segment in the first waveform.
        """
        sub_index = self.orig_sub.find_clicked_id(event)

        # scroll to selected segment
        self.first_frame.selected = sub_index
        try:
            x0, x1 = self.first_frame.segments[int(sub_index)]
        except:
            self.first_frame.selected = None
            return
        
        img_width = x1 - x0
        # offset to make the selected segment appear in the middle of the canvas
        offset = (self.canvas_width - img_width) / 2
        scroll = (x0 - offset) / (len(self.y_coords) / 10)
        self.first_frame.scrollbar.set(scroll, scroll)
        self.highlight_selected(sub_index)

    def sub_click_eventA(self, event):
        """Handles the click event on a speech segment in the second subtitles and highlights the corresponding 
        segment in the second waveform.
        """
        sub_index = self.aligned_sub.find_clicked_id(event)

        # scroll to selected segment
        self.second_frame.selected = sub_index
        try:
            x0, x1 = self.second_frame.segments[int(sub_index)]
        except:
            self.second_frame.selected = None
            return
        
        img_width = x1 - x0
        # offset to make the selected segment appear in the middle of the canvas
        offset = (self.canvas_width - img_width) / 2
        scroll = (x0 - offset) / (len(self.y_coords2) / 10)
        self.second_frame.scrollbar.set(scroll, scroll)
        self.highlight_selectedA(sub_index)

    def draw_waveform1(self, *args):
        """Draws the waveform in the first_frame canvas based on the current scrollbar position. It also 
        creates speech rectangles for the speech segments.
        """
        if self.filename1 == "":
            return
        self.first_frame.canvas.delete("all")
        l1, _ = self.first_frame.scrollbar.get()
        d1 = int(len(self.y_coords) * l1)
        d2 = d1 + self.canvas_width * 10
        self.first_frame.canvas.create_line(*zip(self.x_coords, (self.canvas_height / 2 - self.y_coords[d1:d2])),
                               fill=self.normal_fill)
        if self.srtfilename == "":
            return
        self.first_frame.create_speech_rectangles(d1 / 10, d2 / 10, 1)

    def mark_speech_segments(self):
        """Prepares and displays the speech segments in the first waveform as images with transparency."""
        segments = get_speech_segments(self.srtfilename)
        self.first_frame.segments = segments * (self.sr / 10)
        for seg in self.first_frame.segments:
            self.first_frame.prepare_images(seg[0], 0, seg[1], self.canvas_height, fill="#ff4f19", alpha=.5)
        self.first_frame.create_speech_rectangles(0, self.canvas_width, 1)
        self.first_frame.canvas.tag_bind("speech", "<Button-1>", self.selected_speech_event)
        # print("SIZE OF IMAGES", sys.getsizeof(self.images))

    def selected_speech_event(self, event):
        """Handles the click event on a speech segment in the first waveform and highlights the corresponding 
        segment in the waveform and scrolls to and highlights the corresponding segment in the original subtitles.
        """
        item = event.widget.find_withtag('current')
        tags = self.first_frame.canvas.itemcget(item, "tags")
        id = tags.split(" ")[1]

        self.first_frame.selected = id

        # scroll to deleted
        try:
            print("id", int(id) + 1)
            index = np.where([int(id) + 1 in subarr for subarr in self.grouped])[0]
            print("index", self.signal_mismatch[index])
            offset = self.canvas_width / 2 * 10
            scroll = (self.signal_mismatch[index] - offset) / len(self.y_coords2)
            print("scroll", scroll)
            self.second_frame.scrollbar.set(scroll, scroll)
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
        """Highlights the selected segment in the fisrt subtitles and seeks to the corresponding time in the first video."""
        print("highlighting" + id)

        self.draw_waveform1()

        # seek in video
        x0, _ = self.first_frame.segments[int(id)]
        if self.tkvideo1 != "not_setup":
            self.tkvideo1.seek(x0 * 10 / self.sr)

        self.orig_sub.highlight_sub(id)

    def draw_waveform2(self, *args):
        """Draws the waveform in the second_frame canvas based on the current scrollbar position and 
        creates rectangles for the speech segments.
        """
        if self.filename2 == "":
            return
        self.second_frame.canvas.delete("all")
        l1, _ = self.second_frame.scrollbar.get()
        d1 = int(len(self.y_coords2) * l1)
        d2 = d1 + self.canvas_width * 10
        indices = np.where((d2 >= self.signal_mismatch) & (d1 <= self.signal_mismatch))[0]
        for i in indices:
            x = (self.signal_mismatch[i] - d1) / 10
            self.second_frame.canvas.create_rectangle(x, 0, x + 5, self.canvas_height, fill=self.removed_fill,
                                         outline=self.removed_fill, tags=("removed", str(i)))
        self.second_frame.canvas.create_line(*zip(self.x_coords, (self.canvas_height / 2 - self.y_coords2[d1:d2])),
                                fill=self.normal_fill)
        if self.fname == "":
            return
        self.second_frame.create_speech_rectangles(d1 / 10, d2 / 10, 2)

    def mark_speech_segmentsA(self):
        """Prepares and displays the speech segments in the second waveform as images with transparency."""
        segments = get_speech_segments(self.fname)
        self.second_frame.segments = segments * (self.sr / 10)
        for seg in self.second_frame.segments:
            self.second_frame.prepare_images(seg[0], 0, seg[1], self.canvas_height, fill="#ff4f19", alpha=.5)
        self.second_frame.create_speech_rectangles(0, self.canvas_width, 2)
        self.second_frame.canvas.tag_bind("speech", "<Button-1>", self.selected_speech_eventA)
        self.second_frame.canvas.tag_bind("removed", "<Button-1>", self.selected_speech_eventA)
        # print("SIZE OF IMAGES", sys.getsizeof(self.images))

    def selected_speech_eventA(self, event):
        """Handles the click event on a speech segment in the second waveform and highlights the corresponding 
        segment in the waveform and scrolls to and highlights the corresponding segment in the aligned subtitles.
        """
        item = event.widget.find_withtag('current')
        tags = self.second_frame.canvas.itemcget(item, "tags")
        id = tags.split(" ")[1]

        self.second_frame.selected = id
        print(tags)
        # if a deleted segment is selected (the scene missing from the second video)
        # scroll to segment in first waveform
        if tags.split(" ")[0] == "removed":
            # get the first deleted subtitle
            id_del = self.grouped[int(id)][0]
            x0, x1 = self.first_frame.segments[int(id_del) - 1]
            img_width = x1 - x0
            # offset to make the selected segment appear in the middle of the canvas
            offset = (self.canvas_width - img_width) / 2
            scroll = (x0 - offset) / (len(self.y_coords) / 10)
            self.first_frame.scrollbar.set(scroll, scroll)
            self.draw_waveform1()
            return

        self.highlight_selectedA(id)

        # scroll to subs
        self.aligned_sub.see(id + ".first")
        line = self.aligned_sub.dlineinfo(id + ".first")
        better_offset = 10  # for better visual
        self.aligned_sub.yview_scroll(line[1] - better_offset, 'pixels')

    def highlight_selectedA(self, id):
        """Highlights the selected segment in the second subtitles and seeks to the corresponding time in the second video."""
        print("highlighting" + id)

        self.draw_waveform2()

        # seek in video
        x0, _ = self.second_frame.segments[int(id)]
        if self.tkvideo2 != "not_setup":
            self.tkvideo2.seek(x0 * 10 / self.sr)

        self.aligned_sub.highlight_sub(id)

    def align_event(self):
        """
        Initiates the alignment of the two waveforms.
        """
        # create a new window
        self.toplevel_window = ToplevelWindow(self.appearance_mode_menu.get())
        self.toplevel_window.title("Aligning signals")
        self.toplevel_window.label.configure(text="Aligning signals...")
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
        self.toplevel_window.focus()
        filenames = [self.filename1, self.filename2, self.srtfilename]
        self.removed_indexes, self.signal_mismatch, self.grouped = align(filenames)
        self.first_frame.removed_indexes = self.removed_indexes
        # self.removed_indexes, self.signal_mismatch, self.grouped = align_test()
        self.signal_mismatch = np.array(self.signal_mismatch)
        self.signal_mismatch = self.signal_mismatch * self.sr
        self.aligned_text.configure(text="Subtiles Aligned!")
        self.align_button.configure(state="disabled")
        self.out_srt()
        self.mark_speech_segmentsA()
        self.out_wav()
        # close the window
        self.toplevel_window.destroy()

    def out_srt(self):
        """
        Outputs the aligned SRT file and inserts into the aligned_sub textbox.
        """
        # remove not aligned label
        self.aligned_sub.not_aligned_label.place_forget()
        self.fname = self.filename2.rsplit(".", 1)[0] + ".srt"
        
        # insert subs
        self.aligned_sub.insert_subs(self.fname)
        self.aligned_sub.tag_bind("speech", '<Button-1>', self.sub_click_eventA)
        self.aligned_sub.configure(state="disabled")

        # removed subs   red in original sub text
        self.orig_sub.configure(state="normal")
        for id in self.removed_indexes:
            self.orig_sub.tag_config(str(id - 1), foreground=self.removed_fill)
        self.orig_sub.configure(state="disabled")

    def out_wav(self):
        """
        Helper function that prepares the removed images and redraws the waveforms.
        """
        if len(self.signal_mismatch) == 0:
            return
        self.prepare_removed_images()
        self.draw_waveform1()
        self.draw_waveform2()

    def prepare_removed_images(self):
        """
        Prepares removed images by replacing them with red images of the same size.
        """
        for id in self.removed_indexes:
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
