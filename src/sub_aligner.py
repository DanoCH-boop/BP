import customtkinter
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

        self.srtfilename = ""
        self.filename1 = ""
        self.filename2 = ""

        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../test_images")
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "CustomTkinter_logo_single.png")), size=(26, 26))
        self.large_test_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "large_test_image.png")), size=(500, 150))
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_icon_light.png")), size=(20, 20))
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

        self.switch_mode = customtkinter.CTkSegmentedButton(self.sidebar_frame, corner_radius=10, values=["WAV", "SRT"], height=40,
                                                            command=self.select_frame_by_name)
        self.switch_mode.grid(row=5, column=0, pady=10)
        self.switch_mode.set("WAV")
        
        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # create wave frame
        self.waves_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.waves_frame.grid_columnconfigure(0, weight=1)

        # self.waves_frame_large_image_label = customtkinter.CTkLabel(self.waves_frame, text="", image=self.large_test_image)
        # self.waves_frame_large_image_label.grid(row=0, column=0, padx=20, pady=10)

        # self.waves_frame_button_1 = customtkinter.CTkButton(self.waves_frame, text="", image=self.image_icon_image)
        # self.waves_frame_button_1.grid(row=1, column=0, padx=20, pady=10)
        # self.waves_frame_button_2 = customtkinter.CTkButton(self.waves_frame, text="CTkButton", image=self.image_icon_image, compound="right")
        # self.waves_frame_button_2.grid(row=2, column=0, padx=20, pady=10)
        # self.waves_frame_button_3 = customtkinter.CTkButton(self.waves_frame, text="CTkButton", image=self.image_icon_image, compound="top")
        # self.waves_frame_button_3.grid(row=3, column=0, padx=20, pady=10)
        self.align_button = customtkinter.CTkButton(self.waves_frame, text="Align", width=100, height=50,
                                                    font=customtkinter.CTkFont(size=15), command=self.align_signals, state="disabled")
        self.align_button.grid(row=4, column=0, padx=20, pady=10)

        # create subs frame
        self.subs_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.subs_frame.grid_columnconfigure(1, weight=1)
        self.subs_frame.grid_rowconfigure(1, weight=1) 

        self.orig_sub = customtkinter.CTkTextbox(self.subs_frame, corner_radius=10, text_color=("gray10", "gray90"), width=390, height=400)
        self.orig_sub.insert("0.0", "Original subtitles:\n\n" + "\n"*10 + "\t\tSubtitles not yet loaded!")
        self.orig_sub.grid(row=0, column=0, padx=10, pady=10, stick="w")
        self.orig_sub.configure(state="disabled")

        self.aligned_sub = customtkinter.CTkTextbox(self.subs_frame, corner_radius=10, text_color=("gray10", "gray90"), width=390, height=400)
        self.aligned_sub.insert("0.0", "Aligned subtitles:\n\n" + "\n"*10 + "\t\tSubtitles not yet aligned!")
        self.aligned_sub.grid(row=0, column=1, padx=10, pady=10, stick="e")
        self.aligned_sub.configure(state="disabled")

        # select default frame
        self.select_frame_by_name(self.switch_mode.get())
        self.init_mainWindow()

    
    def init_mainWindow(self):
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
        
        # self.first_frame.grid_rowconfigure(0, weight=1)
        # self.first_frame.grid_columnconfigure(0, weight=1)
        # self.canvas = customtkinter.CTkCanvas(self.first_frame, width=800, height=200, bg="grey20")
        # self.canvas.grid(row=0, column=0)
        # self.canvas.create_line(0,90,800,90, fill="#3a7ebf")
        

    def select_frame_by_name(self, name):
        # set button color for selected button
        # self.chooseFile_btn1.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        # self.chooseFile_btn2.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")
        # self.choose_srtFile.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")
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
        self.filename1 = askopenfilename(filetypes=(('Mp4 files', '*.mp4'),('All files', '*.*')), initialdir=os.getcwd())
        if self.filename1 == "":
            return
        print(self.filename1)
        x_coords, y_coords = convert(self.filename1, self.canvas_width, self.canvas_height)
        self.draw_waveform1(x_coords, y_coords)
        self.check_files()
        
        
    def chooseFile_btn2_event(self):
        self.filename2 = askopenfilename(filetypes=(('Mp4 files', '*.mp4'),('All files', '*.*')), initialdir=os.getcwd())
        if self.filename2 == "":
            return
        print(self.filename2)
        x_coords, y_coords = convert(self.filename2, self.canvas_width, self.canvas_height)
        self.draw_waveform2(x_coords, y_coords)
        self.check_files()


    def choose_srtFile_event(self):
        self.srtfilename = askopenfilename(filetypes=(('SRT files', '*.srt'),('All files', '*.*')), initialdir=os.getcwd())
        if self.srtfilename == "":
            return
        print(self.srtfilename)
        tf = open(self.srtfilename)
        orig_sub_txt = tf.read()
        self.orig_sub.configure(state="normal")
        self.orig_sub.delete("0.0", "end")
        self.orig_sub.insert("0.0", "Original subtitles:\n\n" + orig_sub_txt)
        self.orig_sub.configure(state="disabled")
        self.check_files()


    def draw_waveform1(self, x_coords, y_coords):
        self.first_frame._canvas.delete("all")
        # Draw the waveform
        self.first_frame._canvas.create_line(*zip(x_coords, self.canvas_height / 2 - y_coords), fill="#3a7ebf")


    def draw_waveform2(self, x_coords, y_coords):
        self.second_frame._canvas.delete("all")
        # Draw the waveform
        self.second_frame._canvas.create_line(*zip(x_coords, self.canvas_height / 2 - y_coords), fill="#3a7ebf")

        
    def align_signals(self):
        filenames = [self.filename1, self.filename2, self.srtfilename]
        align(filenames)
        print("Aligned")
        self.out_srt()

    
    def out_srt(self):
        tf = open(self.filename2.rsplit(".", 1)[0] + ".srt")
        out_sub_txt = tf.read()
        self.aligned_sub.configure(state="normal")
        self.aligned_sub.delete("0.0", "end")
        self.aligned_sub.insert("0.0", "Aligned subtitles:\n\n" + out_sub_txt)
        self.aligned_sub.configure(state="disabled")

    
    def check_files(self):
        if self.srtfilename != "" and self.filename1 != "" and self.filename2 != "":
            self.align_button.configure(state="normal")
        
    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)


if __name__ == "__main__":
    app = App()
    app.mainloop()
