import customtkinter
from tkinter.messagebox import showinfo
from tkinter.messagebox import Message
import tkinter as tk
from tkinter import Canvas
from tkinter.filedialog import askopenfilename
import os
from PIL import Image
from convert import convert
from align import align

customtkinter.set_default_color_theme("dark-blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Subtitle aligner v0.1")
        self.geometry("1000x600")
 
        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.srtfilename = "C:/Users/pewdi/Desktop/BP/media/meet2.srt"
        self.filename1 = "C:/Users/pewdi/Desktop/BP/media/meet2.wav"
        self.filename2 = "C:/Users/pewdi/Desktop/BP/media/meet2_trim.wav"
        
        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../test_images")
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "CustomTkinter_logo_single.png")), size=(26, 26))
        self.mp4_icon = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "mp4_ico_dark.png")),
                                                dark_image=Image.open(os.path.join(image_path, "mp4_ico_light.png")), size=(50, 50))
        self.srt_icon = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "srt_ico_dark.png")),
                                                dark_image=Image.open(os.path.join(image_path, "srt_ico_light.png")), size=(50, 50))

        # create navigation frame
        self.sidebar_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.sidebar_frame_label = customtkinter.CTkLabel(self.sidebar_frame, text="SubAligner",
                                                             compound="left", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.sidebar_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.chooseFile_btn1 = customtkinter.CTkButton(self.sidebar_frame, corner_radius=10, height=40, border_spacing=0, text="Mp4 File 1",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.mp4_icon, anchor="w", command=self.chooseFile_btn1_event)
        self.chooseFile_btn1.grid(row=1, column=0, pady=10)

        self.chooseFile_btn2 = customtkinter.CTkButton(self.sidebar_frame, corner_radius=10, height=40, border_spacing=0, text="Mp4 File 2",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.mp4_icon, anchor="w", command=self.chooseFile_btn2_event)
        self.chooseFile_btn2.grid(row=2, column=0, pady=10)

        self.choose_srtFile = customtkinter.CTkButton(self.sidebar_frame, corner_radius=10, height=40, border_spacing=0, text="SRT File",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.srt_icon, anchor="w", command=self.choose_srtFile_event)
        self.choose_srtFile.grid(row=3, column=0, pady=10)
        
        self.clear_btn = customtkinter.CTkButton(self.sidebar_frame, text="Clear", width=100, height=40,
                                                    font=customtkinter.CTkFont(size=15), command=self.clear_window)
        self.clear_btn.grid(row=4, column=0, pady=10, sticky="n")
        
        self.mode_switch = customtkinter.CTkSegmentedButton(self.sidebar_frame, corner_radius=10, values=["Both", "Kept", "Removed"], height=40,
                                                            command=self.out_wav)
        self.mode_switch.grid(row=5, column=0, pady=10)
        self.mode_switch.set("Kept")

        self.switch_mode = customtkinter.CTkSegmentedButton(self.sidebar_frame, corner_radius=10, values=["WAV", "SRT"], height=40,
                                                            command=self.select_frame_by_name)
        self.switch_mode.grid(row=6, column=0, pady=10)
        self.switch_mode.set("WAV")
        
        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=7, column=0, padx=20, pady=20, sticky="s")

        # create wave frame
        self.waves_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.waves_frame.grid_columnconfigure(0, weight=1)

        # create subs frame
        self.subs_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.subs_frame.grid_columnconfigure(1, weight=1)
        self.subs_frame.grid_rowconfigure(1, weight=1) 

        # select default frame
        self.select_frame_by_name(self.switch_mode.get())
        self.init_mainWindow()

    
    def init_mainWindow(self):

        self.crds = {"xcrds1": [], "ycrds1": [], "xcrds2": [], "ycrds2": [], "xcrds3": [], "ycrds3": []}

        # initiate first waveform
        self.first_frame_label = customtkinter.CTkLabel(self.waves_frame, text="first_file.wav")
        self.first_frame_label.grid(row=0, column=0, padx=115, pady=(10,0), sticky="w")

        self.canvas_height = 150
        self.canvas_width = 600
        self.first_frame = customtkinter.CTkFrame(self.waves_frame, corner_radius=10, width=600, height=150)
        self.first_frame._canvas.create_line(0,90,800,90, fill="#3a7ebf")
        self.first_frame.grid(row=1, column=0, padx=10, pady=(0,10))

        # initiate second waveform
        self.second_frame_label = customtkinter.CTkLabel(self.waves_frame, text="second_file.wav")
        self.second_frame_label.grid(row=2, column=0, padx=115, pady=(10,0), sticky="w")

        self.second_frame = customtkinter.CTkFrame(self.waves_frame, corner_radius=10, width=600, height=150)
        self.second_frame._canvas.create_line(0,90,800,90, fill="#3a7ebf")
        self.second_frame.grid(row=3, column=0, padx=10, pady=(0,10))

        # initiate "aligned" button
        self.align_button = customtkinter.CTkButton(self.waves_frame, text="Align", width=100, height=50,
                                                    font=customtkinter.CTkFont(size=15), command=self.align_signals, state="disabled")
        self.align_button.grid(row=4, column=0, padx=20, pady=10)

        # Initiate "Subtitles Aligned!" label
        self.aligned_text = customtkinter.CTkLabel(self.waves_frame, text="")
        self.aligned_text.grid(row=5, column=0, pady=10)

        # initiate subs frame
        self.orig_sub = customtkinter.CTkTextbox(self.subs_frame, corner_radius=10, text_color=("gray10", "gray90"), width=390, height=400)
        self.orig_sub.insert("0.0", "Original subtitles:\n\n" + "\n"*10 + "\t\tSubtitles not yet loaded!")
        self.orig_sub.tag_add("Title", "1.0", "1.20")
        self.orig_sub.tag_config("Title", font=customtkinter.CTkFont(weight="bold", size=16))
        self.orig_sub.grid(row=0, column=0, padx=10, pady=10, stick="w")
        self.orig_sub.configure(state="disabled")

        self.aligned_sub = customtkinter.CTkTextbox(self.subs_frame, corner_radius=10, text_color=("gray10", "gray90"), width=390, height=400)
        self.aligned_sub.insert("0.0", "Aligned subtitles:\n\n" + "\n"*10 + "\t\tSubtitles not yet aligned!")
        self.aligned_sub.tag_add("Title", "1.0", "1.20")
        self.aligned_sub.tag_config("Title", font=customtkinter.CTkFont(weight="bold", size=16))
        self.aligned_sub.grid(row=0, column=1, padx=10, pady=10, stick="e")
        self.aligned_sub.configure(state="disabled")

        self.orig_sub.tag_config("Removed", foreground="red", overstrike=True)
        
        # self.first_frame.grid_rowconfigure(0, weight=1)
        # self.first_frame.grid_columnconfigure(0, weight=1)
        # self.canvas = customtkinter.CTkCanvas(self.first_frame, width=800, height=200, bg="grey20")
        # self.canvas.grid(row=0, column=0)
        # self.canvas.create_line(0,90,800,90, fill="#3a7ebf")
        

    def select_frame_by_name(self, name):

        print("Mode switched to: " + self.switch_mode.get())
        # show selected frame
        if self.switch_mode.get() == "WAV":
            self.waves_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.waves_frame.grid_forget()

        if self.switch_mode.get() == "SRT":
            self.subs_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.subs_frame.grid_forget()

    def chooseFile_btn1_event(self):
        previous1 = self.filename1
        self.filename1 = askopenfilename(filetypes=(('Mp4 files', '*.mp4'),('All files', '*.*')), initialdir=os.getcwd(), title="Choose first Mp4 file")
        if self.filename1 == "":
            self.filename1 = previous1
            # return
        elif self.filename1.rsplit(".", 1)[1] not in ("mp4","wav"):
            showinfo("Wrong file type",f"File \"{self.filename1.rsplit('/', 1)[-1]}\" is not an Mp4 file!")
            return
        
        self.switch_mode.set("WAV")
        self.select_frame_by_name("WAV")
        self.first_frame_label.configure(text=self.filename1.rsplit(".", 1)[0].rsplit("/", 1)[-1]+".wav")
        print(self.filename1)
        x_coords, y_coords, _ = convert(self.filename1, self.canvas_width+200, 300)
        self.draw_waveform1(x_coords, y_coords)
        self.check_files()
        
        
    def chooseFile_btn2_event(self):
        previous2 = self.filename2
        self.filename2 = askopenfilename(filetypes=(('Mp4 files', '*.mp4'),('All files', '*.*')), initialdir=os.getcwd(), title="Choose second Mp4 file")
        if self.filename2 == "":
            self.filename2 = previous2
            # return
        elif self.filename2.rsplit(".", 1)[1] not in ("mp4","wav"):
            showinfo("Wrong file type",f"File \"{self.filename2.rsplit('/', 1)[-1]}\" is not an Mp4 file!")
            return
        self.switch_mode.set("WAV")
        self.select_frame_by_name("WAV")
        self.second_frame_label.configure(text=self.filename2.rsplit(".", 1)[0].rsplit("/", 1)[-1]+".wav")
        print(self.filename2)
        x_coords, y_coords,_ = convert(self.filename2, self.canvas_width+200, 300)
        self.draw_waveform2(x_coords, y_coords)
        self.check_files()


    def choose_srtFile_event(self):
        previousSrt = self.srtfilename
        self.srtfilename = askopenfilename(filetypes=(('SRT files', '*.srt'),('All files', '*.*')), initialdir=os.getcwd(), title="Choose SRT subtitle file")
        if self.srtfilename == "":
            self.srtfilename = previousSrt
            # return
        elif self.srtfilename.rsplit(".", 1)[1] != "srt":
            showinfo("Wrong file type",f"File \"{self.srtfilename.rsplit('/', 1)[-1]}\" is not an SRT file!")
            return
        print(self.srtfilename)
        tf = open(self.srtfilename, encoding="utf8")
        orig_sub_txt = tf.read()
        self.orig_sub.configure(state="normal")
        self.orig_sub.delete("0.0", "end")
        self.orig_sub.insert("0.0", "Original subtitles:\n\n" + orig_sub_txt)
        self.orig_sub.tag_add("Title", "1.0", "1.20")
        self.orig_sub.configure(state="disabled")
        self.switch_mode.set("SRT")
        self.select_frame_by_name("SRT")
        self.check_files()


    def draw_waveform1(self, x_coords, y_coords):
        self.first_frame._canvas.delete("all")
        # Draw the waveform
        self.first_frame._canvas.create_line(*zip(x_coords, (self.canvas_height / 2 - y_coords)+18), fill="#3a7ebf")
        self.first_frame.configure(bg_color="transparent")


    def draw_waveform2(self, x_coords, y_coords):
        self.second_frame._canvas.delete("all")
        # Draw the waveform
        self.second_frame._canvas.create_line(*zip(x_coords, (self.canvas_height / 2 - y_coords)+18), fill="#3a7ebf")
        self.second_frame.configure(bg_color="transparent")

        
    def align_signals(self):
        filenames = [self.filename1, self.filename2, self.srtfilename]
        self.removed_indexes, self.signal_mismatch = align(filenames)
        self.removed_indexes.append((21,24))
        print("Aligned", self.removed_indexes, self.signal_mismatch)
        self.aligned_text.configure(text="Subtiles Aligned!")
        # showinfo("Dialog", "Subtitles Aligned!")
        self.out_srt()
        self.out_wav("Kept")

    
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

    
    def out_wav(self, name):
        # self.third_frame = customtkinter.CTkFrame(self.waves_frame, corner_radius=10, width=600, height=150)
        # self.third_frame.grid(row=4, column=0, padx=10, pady=(10,10))
        if self.mode_switch.get() == "Kept":
            if len(self.crds["xcrds1"]) == 0:
                self.crds["xcrds1"], self.crds["ycrds1"], _ = convert(self.filename1, self.canvas_width+200, 300, self.signal_mismatch, mode="Kept")
            x,y = self.crds["xcrds1"], self.crds["ycrds1"]
            fill = "#3a7ebf"
        elif self.mode_switch.get() == "Removed":
            if len(self.crds["xcrds2"]) == 0:
                self.crds["xcrds2"], self.crds["ycrds2"], _ = convert(self.filename1, self.canvas_width+200, 300, self.signal_mismatch, mode="Removed")
            x,y = self.crds["xcrds2"], self.crds["ycrds2"]
            fill = "#db3737"
        else:
            if len(self.crds["xcrds3"]) == 0:
                self.crds["xcrds3"], self.crds["ycrds3"], self.sr = convert(self.filename1, self.canvas_width+200, 300, self.signal_mismatch, mode="Both")
            x,y = self.crds["xcrds3"], self.crds["ycrds3"]
            fill = "#3a7ebf"
        
        self.second_frame._canvas.delete("all")
        self.second_frame_label.configure(text="Aligned signal:")
        self.second_frame._canvas.create_line(*zip(x, (self.canvas_height / 2 - y)+18), fill=fill)

        if self.mode_switch.get() == "Both":
            for start, end in self.signal_mismatch:
                start_index = int(start * self.sr)
                end_index = int(end * self.sr)
                # start_index = int(start_frame * self.x_scale)
                # end_index = int(end_frame * self.x_scale)
                print(start_index, end_index)
                segment_x = x[start_index:end_index]
                segment_y = self.canvas_height / 2 - y[start_index:end_index]
                self.second_frame._canvas.create_line(*zip(segment_x, segment_y+18), fill="#db3737")

        self.second_frame.configure(bg_color="transparent")


    def check_files(self):
        if self.srtfilename != "" and self.filename1 != "" and self.filename2 != "":
            self.align_button.configure(state="normal")
        

    def clear_window(self):
        self.filename1 = ""
        self.filename2 = ""
        self.srtfilename = ""
        self.first_frame_label.configure(text="")
        self.second_frame_label.configure(text="")
        self.aligned_text.configure(text="")
        self.init_mainWindow()
        

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)


if __name__ == "__main__":
    app = App()
    app.mainloop()
