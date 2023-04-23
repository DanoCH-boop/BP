import customtkinter
from tkinter.messagebox import showinfo
from tkinter.messagebox import Message
import tkinter as tk
from tkinter.filedialog import askopenfilename
import os
from PIL import Image
from misc.convert import convert
from align import align
from misc.speech_segments import get_speech_segments
from tkVideoPlayer import TkinterVideo
import math
import pysrt
import sys
from PIL import Image, ImageTk
from time import sleep

customtkinter.set_default_color_theme("green")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Subtitle aligner v0.1")
        self.geometry("1000x600")
        self.minsize(1000,600)
        # self.geometry("%dx%d+0+0" % (self.winfo_screenwidth(), self.winfo_screenheight()-60))

        # color map
        self.cm = {
            "fr_bg_d": "#2b2b2b",   # frame_background_dark
            "hl_d": "#925827",      # highlight dark
            "vid_bg_d": "#242424",  # video background dark
            "fr_bg_l": "#dbdbdb",   # frame background light
            "hl_l": "#eab17f",      # highlight light
            "vid_bg_l": "#ebebeb"   # video background
        }

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # srtfilename = "../example/example.srt"
        # filename1 = "../example/example.wav"
        # filename2 = "../example/example_trim.wav"

        srtfilename = ""
        filename1 = ""
        filename2 = ""

        self.srtfilename = srtfilename
        self.filename1 = filename1
        self.filename2 = filename2

        self.example_loaded = 1

        self.removed_fill = "#db3737" # red
        self.normal_fill = "#2cbe79"  # green
        
        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../icons")
        self.mp4_icon = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "mp4add_ico_dark.png")),
                                                dark_image=Image.open(os.path.join(image_path, "mp4add_ico_light.png")), size=(65, 65))
        self.srt_icon = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "srtadd_ico_dark.png")),
                                                dark_image=Image.open(os.path.join(image_path, "srtadd_ico_light.png")), size=(65, 65))
        self.add_icon = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "add_dark.png")),
                                                dark_image=Image.open(os.path.join(image_path, "add_light.png")), size=(50, 50))
        self.play_icon = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "play_button.png")), size=(20, 20))
        self.pause_icon = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "pause_button.png")), size=(20, 20))


        # create navigation frame
        self.sidebar_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        self.sidebar_frame_label = customtkinter.CTkLabel(self.sidebar_frame, text="SubAligner",
                                                            compound="left", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.sidebar_frame_label.grid(row=0, column=0, padx=40, pady=20)

        self.chooseFile_btn1 = customtkinter.CTkButton(self.sidebar_frame, corner_radius=10, height=10, border_spacing=0, text="Mp4 File 1",
                                                        fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                        image=self.mp4_icon, anchor="w", command=self.chooseFile_btn1_event)
        self.chooseFile_btn1.grid(row=1, column=0, pady=0)

        self.chooseFile_btn2 = customtkinter.CTkButton(self.sidebar_frame, corner_radius=10, height=10, border_spacing=0, text="Mp4 File 2",
                                                        fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                        image=self.mp4_icon, anchor="w", command=self.chooseFile_btn2_event)
        self.chooseFile_btn2.grid(row=2, column=0, pady=0)

        self.choose_srtFile = customtkinter.CTkButton(self.sidebar_frame, corner_radius=10, height=10, border_spacing=0, text="SRT File",
                                                        fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                        image=self.srt_icon, anchor="w", command=self.choose_srtFile_event)
        self.choose_srtFile.grid(row=3, column=0, pady=0)
        
        self.clear_btn = customtkinter.CTkButton(self.sidebar_frame, text="Clear", width=100, height=40,
                                                    font=customtkinter.CTkFont(size=15), command=self.clear_window)
        self.clear_btn.grid(row=4, column=0, pady=10, sticky="n")
        
        self.mode_switch = customtkinter.CTkOptionMenu(self.sidebar_frame, corner_radius=10, values=["Both", "Kept", "Removed", "Original"],
                                                        command=self.out_wav, width=120, height=30, font=customtkinter.CTkFont(size=14))
        self.mode_switch.grid(row=5, column=0, padx=10, pady=10, sticky="n")
        self.mode_switch.set("Kept")

        #initiate "aligned" button
        self.align_button = customtkinter.CTkButton(self.sidebar_frame, text="Align", width=100, height=40,
                                                    font=customtkinter.CTkFont(size=15), command=self.align_signals, state="disabled")
        self.align_button.grid(row=6, column=0, pady=10)

        # Initiate "Subtitles Aligned!" label
        self.aligned_text = customtkinter.CTkLabel(self.sidebar_frame, text="")
        self.aligned_text.grid(row=7, column=0, pady=(0,10))

        self.switch_mode = customtkinter.CTkSegmentedButton(self.sidebar_frame, corner_radius=10, values=["WAV", "SRT"], height=40)
        self.switch_mode.grid(row=8, column=0, pady=10, sticky="s")
        self.switch_mode.set("WAV")
        
        self.appearance_mode_menu = customtkinter.CTkSwitch(self.sidebar_frame, command=self.change_appearance_mode_event, text="Dark mode",
                                                            switch_height=15, switch_width=35)
        self.appearance_mode_menu.grid(row=9, column=0, padx=20, pady=(10,20), sticky="s")

        # self.rowconfigure(0, weight=3)
        # self.rowconfigure(1, weight=2)

        # create main frame
        self.main_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", pady=0, padx=0)
        self.main_frame.columnconfigure(1, weight=3)
        self.main_frame.columnconfigure(0, weight=2)
        # self.rowconfigure(0, weight=1)
        # self.rowconfigure(1, weight=1)
        
        # # create video frame
        # self.video_frame = customtkinter.CTkFrame(self.main_frame, corner_radius=0, fg_color="blue")
        # self.video_frame.grid(row=0, column=0)

        # # create wave frame
        # self.waves_frame = customtkinter.CTkFrame(self.main_frame, corner_radius=0, fg_color="orange")
        # self.waves_frame.grid(row=0, column=1)

        # create subs frame
        self.subs_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.subs_frame.grid(row=1, column=1, sticky="sew", pady=(0,5), padx=0)
        self.subs_frame.grid_rowconfigure(0, weight=1)
        self.subs_frame.grid_columnconfigure(0, weight=1)
        self.subs_frame.grid_columnconfigure(1, weight=1)

        # self.tkvideo1 = TkinterVideo(master=self.main_frame, background=("#ebebeb"))
        # self.tkvideo1.load(r"C:\Users\pewdi\Desktop\BP\media\Lotr_Rotk_1.mp4")
        # self.tkvideo1.grid(row=0, column=0, sticky="nsew", pady=(10,0), padx=0)
        # self.tkvideo1.set_size((600, 450)) # sets the frame size
        # self.tkvideo1.play() # play the video

        # self.tkvideo2 = TkinterVideo(master=self.main_frame, background=("#ebebeb"))
        # self.tkvideo2.load(r"C:\Users\pewdi\Desktop\BP\media\Lotr_Rotk_1.mp4")
        # self.tkvideo2.grid(row=1, column=0, sticky="nsew", pady=10, padx=0)
        # self.tkvideo2.set_size((600, 450)) # sets the frame size
        # self.tkvideo2.play() # play the video

        # select default frame
        # self.select_frame_by_name(self.switch_mode.get())
        self.init_mainWindow()
        self.state("zoomed")

    
    def init_mainWindow(self):

        self.crds = {"xcrds1": [], "ycrds1": [], "xcrds2": [], "ycrds2": [], "xcrds3": [], "ycrds3": []}
        self.signal_mismatch = []
        self.x_coords2 = []
        self.y_coords2 = []
        self.previous_tag2 = None
        
        # init videos
        self.tkvideo1 = customtkinter.CTkFrame(self.main_frame, fg_color=("#dbdbdb", "#2b2b2b"), corner_radius=10, width=140)
        self.tkvideo1.grid(row=0, column=0, sticky="nsew", pady=(10,0), padx=(10,0))
        self.addvid1 = customtkinter.CTkButton(self.tkvideo1, text="Add Mp4 file", command=self.chooseFile_btn1_event, image=self.add_icon,
                                                fg_color="transparent", hover_color=("gray70", "gray30"), text_color=("gray10", "gray90"),
                                                compound="top")
        self.addvid1.pack(fill="both", expand=True, padx=2, pady=2)
        self.seeker1 = customtkinter.CTkFrame(self.main_frame, fg_color="transparent", corner_radius=10, width=140, height=28)
        self.seeker1.grid(row=1, column=0, sticky="nsew", pady=0, padx=(10,0))
        self.slider1 = customtkinter.CTkSlider(self.seeker1, from_=0, to=1, command=self.seek1, height=15)
        self.slider1.set(0)
        self.slider1.configure(state="disabled")
        self.play_button1 = customtkinter.CTkButton(self.seeker1, image=self.play_icon, text="", fg_color="transparent",
                                                     hover_color=("gray70", "gray30"),
                                                     command=self.play_pause1, width=28)
        self.play_button1.configure(state="disabled")
        self.slider1.grid(row=0, column=1, sticky="ew", pady=(2,2))
        self.play_button1.grid(row=0, column=0, sticky="nsew", padx=(3,3), pady=(2,2))
        self.seeker1.grid_columnconfigure(1, weight=10)
        self.video1 = "not_setup"

        self.tkvideo2 = customtkinter.CTkFrame(self.main_frame, fg_color=("#dbdbdb", "#2b2b2b"), corner_radius=10, width=140)
        self.tkvideo2.grid(row=2, column=0, sticky="nsew", pady=(5,0), padx=(10,0))
        self.addvid2 = customtkinter.CTkButton(self.tkvideo2, text="Add Mp4 file", command=self.chooseFile_btn2_event, image=self.add_icon,
                                                fg_color="transparent", hover_color=("gray70", "gray30"),text_color=("gray10", "gray90"),
                                                compound="top")
        self.addvid2.pack(fill="both", expand=True, padx=2, pady=2)
        self.seeker2 = customtkinter.CTkFrame(self.main_frame, fg_color="transparent", corner_radius=10, width=140, height=28)
        self.seeker2.grid(row=3, column=0, sticky="nsew", pady=(0,10), padx=(10,0))
        self.slider2 = customtkinter.CTkSlider(self.seeker2, from_=0, to=1, command=self.seek1, height=15)
        self.slider2.set(0)
        self.slider2.configure(state="disabled")
        self.play_button2 = customtkinter.CTkButton(self.seeker2, image=self.play_icon, text="", fg_color="transparent",
                                                     hover_color=("gray70", "gray30"),
                                                     command=self.play_pause1, width=28)
        self.play_button2.configure(state="disabled")
        self.slider2.grid(row=0, column=1, sticky="ew", pady=(2,2))
        self.play_button2.grid(row=0, column=0, sticky="nsew", padx=(3,3), pady=(2,2))
        self.seeker2.grid_columnconfigure(1, weight=10)
        self.video2 = "not_setup"

        # initiate first waveform
        # self.first_frame_label = customtkinter.CTkLabel(self.main_frame, text="first_file.wav")
        # self.first_frame_label.grid(row=0, column=1, padx=115, pady=(10,0), sticky="w")

        self.canvas_height = 250
        self.canvas_width = 970
        # self.first_frame = customtkinter.CTkFrame(self.main_frame, corner_radius=10)
        # self.first_frame._canvas.create_line(0,115,1200,115, fill=self.normal_fill)
        # self.first_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.first_frame = customtkinter.CTkScrollableFrame(master=self.main_frame, orientation="horizontal", fg_color=("#dbdbdb", "#2b2b2b"),
                                                             corner_radius=10)
        self.first_frame.grid(row=0, column=1, padx=10, pady=(10,0), sticky="nsew")
        self.first = tk.Canvas(self.first_frame, width=self.canvas_width, height=self.canvas_height, background=("#dbdbdb"),
                                highlightbackground=("#dbdbdb"))
        # self.first2 = tk.Canvas(self.first_frame, width=self.canvas_width, height=self.canvas_height, background=("red"),
                                # highlightbackground=("#dbdbdb"))
        # self.first.grid(column=0, row=0, sticky="nsew")
        # self.first2.grid(column=1, row=0, sticky="nsew")
        # self.first_frame.grid_columnconfigure((0,1), weight=1)


        self.first.pack(expand=True, fill="both")
        # self.first2.pack(expand=True, fill="both")
        self.update()
        self.first.create_line(0,self.first.winfo_height()/2,self.canvas_width,self.first.winfo_height()/2, fill=self.normal_fill)
        # self.first2.create_line(0,self.first.winfo_height()/2,self.canvas_width,self.first.winfo_height()/2, fill="red")


        # initiate second waveform
        # self.second_frame_label = customtkinter.CTkLabel(self.main_frame, text="second_file.wav")
        # self.second_frame_label.grid(row=2, column=0, padx=115, pady=10, sticky="w")

        # self.second_frame = customtkinter.CTkFrame(self.main_frame, corner_radius=10)
        # self.second_frame._canvas.create_line(0,115,1200,115, fill=self.normal_fill)
        # self.second_frame.grid(row=1, column=1, padx=10, pady=0, sticky="nsew")
        self.second_frame = customtkinter.CTkScrollableFrame(master=self.main_frame, orientation="horizontal", fg_color=("#dbdbdb", "#2b2b2b"),
                                                              corner_radius=10)
        self.second_frame.grid(row=2, column=1, padx=10, pady=(5,0), sticky="nsew")
        self.second = tk.Canvas(self.second_frame, width=self.canvas_width, height=self.canvas_height, background=("#dbdbdb"),
                                 highlightbackground=("#dbdbdb"))
        self.second.pack(expand=True, fill="both")
        self.update()
        self.second.create_line(0,self.second.winfo_height()/2,self.canvas_width,self.second.winfo_height()/2, fill=self.normal_fill)
        
        # initiate subs frame
        self.orig_sub = customtkinter.CTkTextbox(self.subs_frame, corner_radius=10, text_color=("gray10", "gray90"), height=260, wrap="none",
                                                 font = customtkinter.CTkFont(family="Consolas"))
        self.orig_sub.insert("0.0", "Original subtitles:")
        self.orig_sub.tag_add("Title", "1.0", "1.20")
        # self.orig_sub.tag_config("Title", font=customtkinter.CTkFont(weight="bold", size=16))
        self.orig_sub.grid(row=0, column=0, padx=10, pady=0, sticky="we")
        self.srt_add = customtkinter.CTkButton(self.orig_sub, text="Add SRT file", command=self.choose_srtFile_event, image=self.add_icon,
                                                fg_color="transparent", hover_color=("gray90", "gray30"), text_color=("gray10", "gray90"),
                                                compound="top")
        self.srt_add.place(relx=.5, rely=.5,anchor="c", relwidth=0.5, relheight=0.5)
        self.orig_sub.configure(state="disabled")

        self.aligned_sub = customtkinter.CTkTextbox(self.subs_frame, corner_radius=10, text_color=("gray10", "gray90"), height=260,
                                                     font = customtkinter.CTkFont(family="Consolas"))
        self.aligned_sub.insert("0.0", "Aligned subtitles:\n\n" + "\n"*8 + "\t\t\t\tSubtitles not yet aligned!")
        self.aligned_sub.tag_add("Title", "1.0", "1.20")
        # self.aligned_sub.tag_config("Title", font=customtkinter.CTkFont(weight="bold", size=16))
        self.aligned_sub.grid(row=0, column=1, padx=10, pady=0, sticky="ew")
        self.aligned_sub.configure(state="disabled")
        
        # # # initiate "aligned" button
        # # self.align_button2 = customtkinter.CTkButton(self.subs_frame, text="Align", width=100, height=50,
        # #                                             font=customtkinter.CTkFont(size=15), command=self.align_signals, state="disabled")
        # # self.align_button2.grid(row=1, padx=20, pady=0, columnspan=2)

        # # # Initiate "Subtitles Aligned!" label
        # # self.aligned_text2 = customtkinter.CTkLabel(self.subs_frame, text="")
        # # self.aligned_text2.grid(row=2, pady=(0,60), columnspan=2)
        self.orig_sub.tag_config("Removed", foreground=self.removed_fill, overstrike=True)
        self.align_button.configure(state="disabled")

        
    # def select_frame_by_name(self, name):

    #     print("Mode switched to: " + name)
    #     # show selected frame
    #     if name == "WAV":
    #         self.waves_frame.grid(row=0, column=1, sticky="nsew")
    #         self.mode_switch.configure(state="normal")
    #         # self.mode_switch.grid(row=5, column=0, pady=10)
    #     else:
    #         self.waves_frame.grid_forget()

    #     if name == "SRT":
    #         self.subs_frame.grid(row=0, column=1, sticky="nsew")
    #         self.mode_switch.configure(state="disabled")
    #         # self.mode_switch.grid_forget()
    #     else:
    #         self.subs_frame.grid_forget()

    def chooseFile_btn1_event(self):
        previous1 = self.filename1

        if self.example_loaded == 1:
            self.filename1 = askopenfilename(filetypes=(('Mp4, WAV files', '*.mp4;*.wav'),('All files', '*.*')), initialdir=os.getcwd(), title="Choose first Mp4 file")

        if self.filename1 == "":
            self.filename1 = previous1
            return
        elif self.filename1.rsplit(".", 1)[1] not in ("mp4","wav"):
            showinfo("Wrong file type",f"File \"{self.filename1.rsplit('/', 1)[-1]}\" is not an Mp4 or a Wav file!")
            return
        
        self.switch_mode.set("WAV")
        # self.select_frame_by_name("WAV")
        # self.first_frame_label.configure(text=self.filename1.rsplit(".", 1)[0].rsplit("/", 1)[-1]+".wav")
        print(self.filename1)
        if self.filename1.rsplit(".", 1)[1] == "mp4":
            self.video1_setup()
        x_coords, y_coords, self.sr = convert(self.filename1, self.canvas_width, self.canvas_height)
        self.draw_waveform1(x_coords, y_coords)
        if self.srtfilename != "":
            self.mark_speech_segments()
        self.check_files()
        
        
    def chooseFile_btn2_event(self):
        previous2 = self.filename2

        if self.example_loaded == 1:
            self.filename2 = askopenfilename(filetypes=(('Mp4, WAV files', '*.mp4;*.wav'),('All files', '*.*')), initialdir=os.getcwd(), title="Choose second Mp4 file")

        if self.filename2 == "":
            self.filename2 = previous2
            return
        elif self.filename2.rsplit(".", 1)[1] not in ("mp4","wav"):
            showinfo("Wrong file type",f"File \"{self.filename2.rsplit('/', 1)[-1]}\" is not an Mp4 file!")
            return
        self.switch_mode.set("WAV")
        # self.select_frame_by_name("WAV")
        # self.second_frame_label.configure(text=self.filename2.rsplit(".", 1)[0].rsplit("/", 1)[-1]+".wav")
        print(self.filename2)
        self.video2_setup()
        self.x_coords2, self.y_coords2,_ = convert(self.filename2, self.canvas_width, self.canvas_height)
        self.draw_waveform2()
        self.check_files()


    def choose_srtFile_event(self):
        previousSrt = self.srtfilename
        
        if self.example_loaded == 1:
            self.srtfilename = askopenfilename(filetypes=(('SRT files', '*.srt'),('All files', '*.*')), initialdir=os.getcwd(), title="Choose SRT subtitle file")
        
        if self.srtfilename == "":
            self.srtfilename = previousSrt
            return
        elif self.srtfilename.rsplit(".", 1)[1] != "srt":
            showinfo("Wrong file type",f"File \"{self.srtfilename.rsplit('/', 1)[-1]}\" is not an SRT file!")
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
            if sub.index in (10,100,1000):
                index_len -= 1
            num_time_first = ' ' * index_len  + '   '.join(str(sub).split('\n')[:3])
            sub_width = len(num_time_first)  - len(sub.text.split("\n", 1)[0])
            other_lines = [' ' * sub_width + line for line in str(sub).splitlines()[3:]]
            processed_sub = num_time_first + '\n' + '\n'.join(other_lines)
            if processed_sub[-1] != "\n":
                processed_sub += "\n"
            processed_sub += "\n"
            self.orig_sub.insert("end", processed_sub, ("speech", str(sub.index-1)))
            self.orig_sub.tag_bind(str(sub.index-1), "<Enter>", self.on_enter_sub)
            self.orig_sub.tag_bind(str(sub.index-1), "<Leave>", self.on_leave_sub)

        
    def on_enter_sub(self, event):
        index = self.orig_sub.index("@%s,%s" % (event.x, event.y))
        tags = self.orig_sub.tag_names(index)
        self.previous_tag1 = tags[1]
        if self.orig_sub.tag_cget(tags[1], "background") in ("#eab17f","#925827"):
            return
        event.widget.tag_configure(tags[1], background="#dbdbdb")
        if self.appearance_mode_menu.get() == 1:
            event.widget.tag_configure(tags[1], background="#2b2b2b")

    
    def on_leave_sub(self, event):
        if self.orig_sub.tag_cget(self.previous_tag1, "background") in ("#eab17f","#925827"):
            return
        event.widget.tag_configure(self.previous_tag1, background="")
        event.widget.tag_configure("speech", background="")
        
 
    #https://stackoverflow.com/a/24145562
    def sub_click_event(self, event):                
        index = self.orig_sub.index("@%s,%s" % (event.x, event.y))
        tags = self.orig_sub.tag_names(index)
        sub_index = tags[1]
        # if the text is highlited by dragging the mouse tags = ("sel", "speech", "id"), we want sub_index = id
        if sub_index == "speech":
            sub_index = tags[2]

        x1, x2 = self.highlight_selected(sub_index)

        # scroll to segment
        img_width = x2 - x1
        x,y = self.first_frame._scrollbar.get()
        visible_width = (y - x)*self.first.winfo_width() - img_width
        x_scroll = x1 - visible_width/2
        self.first_frame._parent_canvas.xview_moveto(x_scroll/self.first.winfo_width())
    

    def video1_setup(self):
        bg = "#ebebeb"
        if self.appearance_mode_menu.get() == 1:
            bg = "#242424"
        self.play_button1.configure(state="normal")
        self.slider1.configure(state="normal")
        self.slider1.set(0)
        self.play_button1.configure(image=self.play_icon)
        self.addvid1.pack_forget()
        if self.video1 != "not_setup":
            self.video1.pack_forget()
        self.video1 = TkinterVideo(master=self.tkvideo1, background=bg, text="Click play to play video!", font=customtkinter.CTkFont(size=20))
        self.video1.load(self.filename1)
        self.video1.pack(fill="both", expand=True) 
        # self.video1.set_size((600, 450)) # sets the frame size
        self.video1.bind("<<Duration>>", self.update_duration)
        self.video1.bind("<<SecondChanged>>", self.update_slider)
        self.video1.bind("<<Ended>>", self.video_ended)


    def video2_setup(self):
        bg = "#ebebeb"
        if self.appearance_mode_menu.get() == 1:
            bg = "#242424"
        self.tkvideo2 = TkinterVideo(master=self.main_frame, background=bg)
        self.tkvideo2.load(self.filename2)
        self.tkvideo2.grid(row=1, column=0, sticky="nsew", pady=10, padx=0)
        self.tkvideo2.set_size((600, 450)) # sets the frame size
        self.tkvideo2.play() # play the video


    def update_duration(self, event):
        """ updates the duration after finding the duration """
        print("here1")
        duration = self.video1.video_info()["duration"]
        # end_time["text"] = str(datetime.timedelta(seconds=duration))
        self.slider1.configure(to=duration)
        print(duration)


    def seek1(self, val):
        print("seeked to:", int(val))
        self.video1.seek(math.ceil(val))
        if self.video1.is_paused():
            self.video1.play()
            self.video1.pause()
        

    def play_pause1(self):
        if self.video1.is_paused():
            print("paused")
            self.video1.play()
            self.play_button1.configure(image=self.pause_icon)
            return
        print("not paused")
        self.video1.pause()
        self.play_button1.configure(image=self.play_icon)

    
    def update_slider(self, event):
        print(self.video1.current_duration())
        self.slider1.set(self.video1.current_duration())


    def video_ended (self, event):
        self.slider1.set(0)
        self.play_button1.configure(image=self.play_icon)


    def draw_waveform1(self, x_coords, y_coords):
        self.first.delete("all")
        width = len(x_coords) / 10
        print("1",width)
        print("x", len(x_coords), "y", len(y_coords))
        # width = math.ceil(width / 100) * 100
        # print("1",width)
        # Draw the waveform
        cap = 31000
        self.first.configure(width=width)

        limit = math.ceil(width / cap)
        # for i in range(1, limit+1):
        #     print("cap", cap*10*(i-1), cap*10*i)
        #     self.first.create_line(*zip(x_coords[cap*10*(i-1):cap*10*i], (self.canvas_height / 2 - y_coords[cap*10*(i-1):cap*10*i])), fill=self.normal_fill)
        # self.first.create_line(*zip(x_coords, (self.canvas_height / 2 - y_coords)), fill=self.normal_fill)
        self.first.create_line(*zip(x_coords, (250 / 2 - y_coords)), fill=self.normal_fill)


        # self.first.create_line(*zip(x_coords, (self.canvas_height / 2 - y_coords)), fill=self.normal_fill)


    def mark_speech_segments(self):
        segments = get_speech_segments(self.srtfilename)
        segments = segments*(self.sr/10)
        self.images = []
        for id, seg in enumerate(segments):
            self.create_rectangle(seg[0]*self.sr/10, 0, seg[1]*self.sr/10, self.canvas_height, fill="#ff4f19", alpha=.5, outline="orange",
                                  tags=("speech", str(id)))
            
        self.first.tag_bind("speech", "<Button-1>", self.selected_speech_event)
        print("SIZE OF IMAGES", sys.getsizeof(self.images))


    def selected_speech_event(self, event):
        item = event.widget.find_withtag('current')
        tags = self.first.itemcget(item, "tags")
        id = tags.split(" ")[1]

        self.highlight_selected(id)

        # scroll to subs
        self.orig_sub.see(id+".first")
        line = self.orig_sub.dlineinfo(id+".first")
        better_offset = 10
        self.orig_sub.yview_scroll(line[1]-better_offset, 'pixels')


    def highlight_selected(self, id):
        print("highlighting" + id) 
        # find selected (image) segment and the previous clicked segment
        speech_seg = self.first.find_withtag('speech&&'+ id)
        previous_seg = self.first.find_withtag("selected")
        # delete previous segment highlighting
        if len(previous_seg) != 0:
            # not working, probably because the new item puts itself underneath the original one, so its never the one selected
            # if previous_seg[0] == speech_seg[0]:
            #     print("same seg selected",  previous_seg[0], speech_seg[0])
            #     return
        
            for prev_seg in previous_seg:
                self.first.delete(prev_seg)
        # create new highlighting
        x1,_,x2,_ = self.first.coords(speech_seg[2])
        self.create_rectangle(x1, 0, x2, self.canvas_height, fill="#ff4f19", alpha=.5, tags=("speech", id, "selected"), outline="orange")
        # erase previous subtitle highlting
        if self.previous_tag2 != None:
            self.orig_sub.tag_config(self.previous_tag2 , background="")
        self.previous_tag2 = id
        # and create new sub highliting
        self.orig_sub.tag_config(id, background="#eab17f")
        if self.appearance_mode_menu.get() == 1:
            self.orig_sub.tag_config(id, background="#925827")

        return x1, x2


    def draw_waveform2(self):
        self.second.delete("all")
        width = len(self.x_coords2)/10
        print("2",width)
        # width = math.ceil(width / 100) * 100
        # print("2",width)
        # Draw the waveform
        self.second.configure(width=width)
        self.second.create_line(*zip(self.x_coords2, (self.canvas_height / 2 - self.y_coords2)), fill=self.normal_fill)
        # self.second_frame.configure(bg_color="transparent")


    def align_signals(self):
        filenames = [self.filename1, self.filename2, self.srtfilename]
        self.removed_indexes, self.signal_mismatch = align(filenames)
        print("Aligned", self.removed_indexes, self.signal_mismatch)
        self.aligned_text.configure(text="Subtiles Aligned!")
        # self.aligned_text2.configure(text="Subtiles Aligned!")
        # showinfo("Dialog", "Subtitles Aligned!")
        self.align_button.configure(state="disabled")
        # self.align_button2.configure(state="disabled")
        # self.mark_speech_semnets()
        self.out_srt()
        self.out_wav(self.mode_switch.get())

    
    def out_srt(self):
        tf = open(self.filename2.rsplit(".", 1)[0] + ".srt", encoding="utf8")
        out_sub_txt = tf.read()
        self.aligned_sub.configure(state="normal")
        self.aligned_sub.delete("0.0", "end")
        self.aligned_sub.insert("0.0", "Aligned subtitles:\n\n" + out_sub_txt)
        self.aligned_sub.tag_add("Title", "1.0", "1.20")
        self.aligned_sub.configure(state="disabled")

        self.orig_sub.configure(state="normal")
        for index in self.removed_indexes:
            self.orig_sub.tag_add("Removed", str(index[0]+2)+".0", str(index[1]+2)+".0")
        self.orig_sub.configure(state="disabled")

    
    def out_wav(self, mode):
        # self.third_frame = customtkinter.CTkFrame(self.waves_frame, corner_radius=10, width=600, height=150)
        # self.third_frame.grid(row=4, column=0, padx=10, pady=(10,10))

        if(len(self.signal_mismatch) == 0):
            return
        
        # if mode == "Original":
        #     self.draw_waveform2()
        #     self.second_frame_label.configure(text=self.filename2.rsplit(".", 1)[0].rsplit("/", 1)[-1]+".wav")
        #     return
        
        # self.second_frame_label.configure(text="Aligned signal:")

        # if mode == "Kept":
        #     if len(self.crds["xcrds1"]) == 0:
        #         self.crds["xcrds1"], self.crds["ycrds1"], _ = convert(self.filename1, self.canvas_width+200, 300, self.signal_mismatch, mode=mode)
        #     x,y = self.crds["xcrds1"], self.crds["ycrds1"]
        #     fill = self.normal_fill
        # elif mode == "Removed":
        #     if len(self.crds["xcrds2"]) == 0:
        #         self.crds["xcrds2"], self.crds["ycrds2"], _ = convert(self.filename1, self.canvas_width+200, 300, self.signal_mismatch, mode=mode)
        #     x,y = self.crds["xcrds2"], self.crds["ycrds2"]
        #     fill = self.removed_fill
        # else:
        #     if len(self.crds["xcrds3"]) == 0:
        #         self.crds["xcrds3"], self.crds["ycrds3"], self.sr = convert(self.filename1, self.canvas_width+200, 300, self.signal_mismatch, mode=mode)
        #     x,y = self.crds["xcrds3"], self.crds["ycrds3"]
        #     fill = self.normal_fill
        
        # self.second_frame._canvas.delete("all")
        # self.second_frame_label.configure(text="Aligned signal:")
        # self.second_frame._canvas.create_line(*zip(x, (self.canvas_height / 2 - y)+18), fill=fill)

        # if mode == "Both":
        #     for start, end in self.signal_mismatch:
        #         start_index = int(start * self.sr)
        #         end_index = int(end * self.sr)
        #         # start_index = int(start_frame * self.x_scale)
        #         # end_index = int(end_frame * self.x_scale)
        #         print(start_index, end_index)
        #         segment_x = x[start_index:end_index]
        #         segment_y = self.canvas_height / 2 - y[start_index:end_index]
        #         self.second_frame._canvas.create_line(*zip(segment_x, segment_y+18), fill=self.removed_fill)

        # self.second_frame.configure(bg_color="transparent")


    # https://stackoverflow.com/a/54645103
    def create_rectangle(self, x1, y1, x2, y2, **kwargs):
        if 'alpha' in kwargs:
            alpha = int(kwargs.pop('alpha') * 255)
            fill = kwargs.pop('fill')
            orange_color = (250, 135, 35)
            fill = orange_color + (alpha,)
            image = Image.new('RGBA', (int(x2-x1)+1, int(y2-y1)+1), fill)
            self.images.append(ImageTk.PhotoImage(image))
            tags = kwargs["tags"]
            self.first.create_image(x1, y1, image=self.images[-1], anchor='nw', tags=tags)
            self.first.create_text(x1+(x2-x1)/2, self.canvas_height/2, text=str(int(tags[1])+1), tags=tags, fill="white",
                                    font=customtkinter.CTkFont(size=25, weight="bold"))
        self.first.create_rectangle(x1, y1, x2, y2, **kwargs)
        

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

        # self.first_frame_label.configure(text="")
        # self.second_frame_label.configure(text="")
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
            except:
                print("subs not yet loaded")
            try:
                self.tkvideo1.configure(background="#242424", highlightbackground="#242424")
                self.tkvideo2.configure(background="#242424", highlightbackground="#242424")
            finally:
                return
        customtkinter.set_appearance_mode("light")
        self.first.configure(background="#dbdbdb", highlightbackground="#dbdbdb")
        self.second.configure(background="#dbdbdb", highlightbackground="#dbdbdb")
        try:   
            self.orig_sub.tag_config(self.previous_tag2, background="#eab17f")
        except:
            print("subs not yet loaded")
        try:
            self.tkvideo1.configure(background="#ebebeb", highlightbackground="#ebebeb")
            self.tkvideo2.configure(background="#ebebeb", highlightbackground="#ebebeb")
        finally:
            return

if __name__ == "__main__":
    app = App()
    app.mainloop()
