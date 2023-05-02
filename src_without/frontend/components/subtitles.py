import customtkinter
import pysrt
from misc.process_sub import process_sub


class SubClass(customtkinter.CTkTextbox):
    def __init__(self, *args, mode, frame, appr, **kwargs):
        super().__init__(*args, **kwargs)
        self.appr = appr
        self.frame = frame
        self.previous_tag2 = None
        if mode == "in":
            self.label = "Original subtitles:\n"
            self.srt_add = customtkinter.CTkButton(self, text="Add SRT file",
                                                fg_color="transparent", hover_color=("gray90", "gray30"),
                                                text_color=("gray10", "gray90"),
                                                compound="top")
            self.srt_add.place(relx=.5, rely=.5, anchor="c", relwidth=0.5, relheight=0.5)
        else:
            self.label = "Aligned subtitles:\n"
            self.not_aligned_label = customtkinter.CTkLabel(self, text="Subtitles not yet aligned!")
            self.not_aligned_label.place(relx=0.5, rely=0.5, anchor="c")

        self.insert("0.0", self.label)
        self.configure(state="disabled")

    def insert_subs(self, srtfilename):
        """
        Insert each processed sub into the sutitle textbox
        """
        self.configure(state="normal")
        self.delete("0.0", "end")
        self.insert("0.0", self.label)
        subs = pysrt.open(srtfilename)
        # reindexes subs after shifting
        subs.clean_indexes()
        index_len = len(str(len(subs)))
        self.insert("end", "\n")
        for sub in subs:
            if sub.index in (10, 100, 1000):
                index_len -= 1
            processed_sub = process_sub(sub, index_len)
            self.insert("end", processed_sub, ("speech", str(sub.index - 1)))
            self.tag_bind(str(sub.index - 1), "<Enter>", self.on_enter_sub)
            self.tag_bind(str(sub.index - 1), "<Leave>", self.on_leave_sub)
        self.tag_config("speech")

    def on_enter_sub(self, event):
        """Handle the hover over enter event for subtitle"""
        index = self.index("@%s,%s" % (event.x, event.y))
        tags = self.tag_names(index)
        self.previous_tag1 = tags[1]
        # if the subtitle you are hovering over is selected, do nothing
        if self.tag_cget(tags[1], "background") in ("#eab17f", "#925827"):
            return
        event.widget.tag_configure(tags[1], background="#dbdbdb")
        if self.appr == 1:
            event.widget.tag_configure(tags[1], background="#2b2b2b")

    def on_leave_sub(self, event):
        """Handle the hover leave end event for subtitle"""
        if self.tag_cget(self.previous_tag1, "background") in ("#eab17f", "#925827"):
            return
        event.widget.tag_configure(self.previous_tag1, background="")
        # event.widget.tag_configure("speech", background="")

    def find_clicked_id(self, event):
        """Finds the id of a clicked sub and returns it"""
        index = self.index("@%s,%s" % (event.x, event.y))
        tags = self.tag_names(index)
        sub_index = tags[1]
        # if the text is highlighted by dragging the mouse, tag sel is added to tags = ("sel", "speech", "id"), we want sub_index = id
        if sub_index == "speech":
            sub_index = tags[2]

        return sub_index
        
    def highlight_sub(self, id):
        """Highlights clicked sub by id"""
        # erase previous subtitle highlting
        if self.previous_tag2 is not None:
            self.tag_config(self.previous_tag2, background="")
        self.previous_tag2 = id
        # and create new sub highliting
        self.tag_config(id, background="#eab17f")
        if self.appr == 1:
            self.tag_config(id, background="#925827")

    def sub_click_event(self, event):
        """Handles the click event on a speech segment in the first subtitles and highlights the corresponding 
        segment in the first waveform.
        """
        sub_index = self.find_clicked_id(event)
        self.highlight_sub(sub_index)
        # scroll to selected segment
        self.frame.selected = sub_index
        try:
            x0, x1 = self.frame.segments[int(sub_index)]
        except:
            self.frame.selected = None
            return
        
        img_width = x1 - x0
        # offset to make the selected segment appear in the middle of the canvas
        offset = (self.frame.canvas_width - img_width) / 2
        scroll = (x0 - offset) / (len(self.frame.y_coords) / 10)
        self.frame.scrollbar.set(scroll, scroll)
        self.frame.highlight_selected(sub_index)
        