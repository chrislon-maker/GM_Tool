from Role_checks import *
import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import filedialog
import os

Klatu_link = 'Klatu3.pdf'
eisgeist_link = 'https://dsa.ulisses-regelwiki.de/Best_Eisgeist.html'


#_COLORS____________________________________________________________________________________________
'''
Color theme
button color:           #1f6aa5 (blue theme)
button hover color:     #3b8ed0
button text color:      #ffffff
background:             #1c1c1c
'''

teal = "#187381"
teal_light = "#209AAC"

red="#96031A"
red_hover="#C80421"
red_light="#FF4040"

orange = "#FF7D00"

violet = "#C490D1"

#green_light = "#7FB685"
green_light = "#5DA265"
green = "#4A8251"

yellow = "#F5B700"

grey_light = "#888888"

ctk.set_appearance_mode("dark") 


#_IMAGES_&_ICONS_______________________________________________________________________________________
plus_icon = "\u2795"

trash_icon = ctk.CTkImage(Image.open("res/trash_icon_white.png"), size=(16, 16))

patch_icon = ctk.CTkImage(Image.open("res/patch_icon.png"), size=(20, 20))
sword_icon = ctk.CTkImage(Image.open("res/sword_icon.png"), size=(20, 20))

arrow_down_icon = ctk.CTkImage(Image.open("res/arrow_down.png"), size=(16, 7))
arrow_up_icon = ctk.CTkImage(Image.open("res/arrow_up.png"), size=(16, 7))

MU_icon = ctk.CTkImage(Image.open("res/MU_icon.png"), size=(35, 35))
KL_icon = ctk.CTkImage(Image.open("res/KL_icon.png"), size=(35, 35))
IN_icon = ctk.CTkImage(Image.open("res/IN_icon.png"), size=(40, 32))
CH_icon = ctk.CTkImage(Image.open("res/CH_icon.png"), size=(35, 35))
FF_icon = ctk.CTkImage(Image.open("res/FF_icon.png"), size=(40, 35))
GE_icon = ctk.CTkImage(Image.open("res/GE_icon.png"), size=(44, 40))
KO_icon = ctk.CTkImage(Image.open("res/KO_icon.png"), size=(35, 35))
KK_icon = ctk.CTkImage(Image.open("res/KK_icon.png"), size=(35, 35))

# --- Tooltip class ---
class Tooltip:
    def __init__(self, widget, text, delay=500, offset=(10, 10)):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.offset = offset
        self.tooltip_window = None
        self.after_id = None

        # Bind hover events
        self.widget.bind("<Enter>", self.schedule)
        self.widget.bind("<Leave>", self.hide_tooltip)
        self.widget.bind("<Motion>", self.update_position)

    def schedule(self, event=None):
        # Schedule tooltip after delay (milliseconds)
        self.after_id = self.widget.after(self.delay, self.show_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return

        x = self.widget.winfo_rootx() + self.offset[0]
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + self.offset[1]

        self.tooltip_window = ctk.CTkToplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = ctk.CTkLabel(
            self.tooltip_window,
            text=self.text,
            fg_color="#333333",
            text_color="white",
            corner_radius=6,
            padx=8,
            pady=4,
        )
        label.pack()

    def hide_tooltip(self, event=None):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def update_position(self, event):
        if self.tooltip_window:
            x = self.widget.winfo_rootx() + event.x + self.offset[0]
            y = self.widget.winfo_rooty() + event.y + self.offset[1]
            self.tooltip_window.geometry(f"+{x}+{y}")

# --- Expandable frame class ---
class ExpandableFrame(ctk.CTkFrame):
    def __init__(self, master, text, font=('Quicksand', 16, 'bold'), **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(1, weight=1)

        # caption
        caption = ctk.CTkLabel(self, text=text, font=font)
        caption.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # button to show and hide the content subframe
        self.toggle_button = ctk.CTkButton(self, text='', image=arrow_down_icon, anchor="w", fg_color=self.cget("fg_color"), hover_color=self.cget("fg_color"), command=self.toggle_frame)
        self.toggle_button.grid(row=0, column=1 , padx=5, pady=5, sticky="w")

        # subframe to be hidden or shown
        self.content = ctk.CTkFrame(self, fg_color=self.cget("fg_color"))
        self.content.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="new")

        self.content.grid_remove() 

    # Function to toggle visibility
    def toggle_frame(self):
        if self.content.winfo_viewable():  # Check if frame is visible
            self.content.grid_remove()     # Hide it
            self.toggle_button.configure(image=arrow_down_icon)
        else:
            self.content.grid()            # Show it
            self.toggle_button.configure(image=arrow_up_icon)

# --- Character frame class ---
class CharacterFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.init_label = ctk.CTkLabel(self, text="Wähle einen Charakter aus...", text_color="#999999", font=('Quicksand', 16, 'italic'))
        self.init_label.pack(expand=True, padx=10, pady=5, fill="both")

    def create(self, char):
        self.init_label.destroy()
        
        ### NAME
        for i in range(8):
            self.grid_columnconfigure(i, weight=1)

        self.name = ctk.CTkLabel(self, text="{:}".format(char.name), font=('Quicksand', 22, 'bold'))
        self.name.grid(row=0, column=0, columnspan=8, pady=5, padx=5, sticky="ew")


        # Attributes
        self.attribute_frame = ctk.CTkFrame(self, height=30, fg_color="#444444")
        self.attribute_frame.grid(row=1, column=0, columnspan=8, padx=5, pady=5, sticky="new")

        for col in range(8):
            self.attribute_frame.grid_columnconfigure(col, weight=1)

        #self.MU = ctk.CTkLabel(self.attribute_frame, corner_radius=5, fg_color=red, text="MU {:}".format(char.MU), font=('Quicksand', 30))
        self.MU = ctk.CTkLabel(self.attribute_frame, image=MU_icon, compound="left", text_color=red_light, padx=5, text="{:}".format(char.MU), font=('Quicksand', 45, 'bold'))
        self.MU.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        Tooltip(self.MU, "Mut (MU) des Charakters")

        #self.KL = ctk.CTkLabel(self.attribute_frame, corner_radius=5, fg_color="purple", text="KL {:}".format(char.KL), font=('Quicksand', 45, 'bold'))
        self.KL = ctk.CTkLabel(self.attribute_frame, image=KL_icon, compound="left", text_color=violet, padx=5, text="{:}".format(char.KL), font=('Quicksand', 45, 'bold'))
        self.KL.grid(row=0, column=1 , padx=5, pady=5, sticky="ew")
        Tooltip(self.KL, "Klugheit (KL) des Charakters")

        #self.IN = ctk.CTkLabel(self.attribute_frame, corner_radius=5, fg_color="green", text="IN {:}".format(char.IN), font=('Quicksand', 45, 'bold'))
        self.IN = ctk.CTkLabel(self.attribute_frame, image=IN_icon, compound="left", text_color=green_light, padx=5, text="{:}".format(char.IN), font=('Quicksand', 45, 'bold'))
        self.IN.grid(row=0, column=2 , padx=5, pady=5,sticky="ew")
        Tooltip(self.IN, "Intuition (IN) des Charakters")

        #self.CH = ctk.CTkLabel(self.attribute_frame, corner_radius=5, fg_color="black", text="CH {:}".format(char.CH), font=('Quicksand', 45, 'bold'))
        self.CH = ctk.CTkLabel(self.attribute_frame, image=CH_icon, compound="left", text_color=grey_light, padx=5, text="{:}".format(char.CH), font=('Quicksand', 45, 'bold'))
        self.CH.grid(row=0, column=3 , padx=5, pady=5,sticky="ew")
        Tooltip(self.CH, "Charisma (CH) des Charakters")

        #self.FF = ctk.CTkLabel(self.attribute_frame, corner_radius=5, fg_color="#B8860B", text="FF {:}".format(char.FF), font=('Quicksand', 45, 'bold'))
        self.FF = ctk.CTkLabel(self.attribute_frame, image=FF_icon, compound="left", text_color=yellow, padx=5, text="{:}".format(char.FF), font=('Quicksand', 45, 'bold'))
        self.FF.grid(row=0, column=4 , padx=5, pady=5,sticky="ew")
        Tooltip(self.FF, "Fingerfertigkeit (FF) des Charakters")

        #self.GE = ctk.CTkLabel(self.attribute_frame, corner_radius=5, fg_color="blue", text="GE {:}".format(char.GE), font=('Quicksand', 45, 'bold'))
        self.GE = ctk.CTkLabel(self.attribute_frame, image=GE_icon, compound="left", text_color=teal_light, padx=5, text="{:}".format(char.GE), font=('Quicksand', 45, 'bold'))
        self.GE.grid(row=0, column=5 , padx=5, pady=5,sticky="ew")
        Tooltip(self.GE, "Geschicklichkeit (GE) des Charakters")

        #self.KO = ctk.CTkLabel(self.attribute_frame, corner_radius=5, fg_color="#666666", text="KO {:}".format(char.KO), font=('Quicksand', 45, 'bold'))
        self.KO = ctk.CTkLabel(self.attribute_frame, image=KO_icon, compound="left", padx=5, text="{:}".format(char.KO), font=('Quicksand', 45, 'bold'))
        self.KO.grid(row=0, column=6 , padx=5, pady=5,sticky="ew")
        Tooltip(self.KO, "Konstitution (KO) des Charakters")

        #self.KK = ctk.CTkLabel(self.attribute_frame, corner_radius=5, fg_color="#CC7000", text="KK {:}".format(char.KK), font=('Quicksand', 45, 'bold'))
        self.KK = ctk.CTkLabel(self.attribute_frame, image=KK_icon, compound="left", padx=5, text_color=orange, text="{:}".format(char.KK), font=('Quicksand', 45, 'bold'))
        self.KK.grid(row=0, column=7 , padx=5, pady=5, sticky="ew")
        Tooltip(self.KK, "Körperkraft (KK) des Charakters")

        # LeP and AsP
        self.LePAsP_frame = ctk.CTkFrame(self, fg_color="#444444")
        self.LePAsP_frame.grid(row=2, column=0, columnspan=8, padx=5, pady=5, sticky="new")

        self.LePAsP_frame.grid_columnconfigure(1, weight=1)

        # LeP
        self.LeP_label = ctk.CTkLabel(self.LePAsP_frame, text="LeP", font=('Quicksand', 16))
        self.LeP_label.grid(row=0, column=0 , padx=5, pady=5,sticky="ew")
        self.LeP_PGbar = ctk.CTkProgressBar(self.LePAsP_frame, progress_color=red_light, width=0, height=10)
        self.LeP_PGbar.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.LeP_PGbar.set(char.LeP/char.maxLeP)
        self.LeP_value = ctk.CTkLabel(self.LePAsP_frame, text="{0:}/{1:}".format(char.LeP, char.maxLeP), font=('Quicksand', 16))
        self.LeP_value.grid(row=0, column=2 , padx=5, pady=5,sticky="ew")

        self.dmg_btn = ctk.CTkButton(self.LePAsP_frame, text='', image=sword_icon, fg_color=red, hover_color=red_light, width=1, command = lambda : DamageToplevel(self, char))
        self.dmg_btn.grid(row=0, column=3 , padx=5, pady=5,sticky="e")
        Tooltip(self.dmg_btn, "Füge Schaden zu")
        self.heal_btn = ctk.CTkButton(self.LePAsP_frame, text='', image=patch_icon, fg_color=green, hover_color=green_light, width=1, command = lambda : HealToplevel(self, char))
        self.heal_btn.grid(row=0, column=4 , padx=5, pady=5,sticky="e")
        Tooltip(self.heal_btn, "Heile LeP")

        # AsP
        self.AsP_label = ctk.CTkLabel(self.LePAsP_frame, text="AsP", font=('Quicksand', 16))
        self.AsP_label.grid(row=1, column=0 , padx=5, pady=5,sticky="ew")
        self.AsP_PGbar = ctk.CTkProgressBar(self.LePAsP_frame, progress_color=teal_light, width=0, height=10)
        self.AsP_PGbar.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        if char.maxAsP == 0:
            self.AsP_PGbar.set(0)
        else:
            self.AsP_PGbar.set(char.AsP/char.maxAsP)
        self.AsP_value = ctk.CTkLabel(self.LePAsP_frame, text="{0:}/{1:}".format(char.AsP, char.maxAsP), font=('Quicksand', 16))
        self.AsP_value.grid(row=1, column=2 , padx=5, pady=5,sticky="ew")

        # KaP
        self.KaP_label = ctk.CTkLabel(self.LePAsP_frame, text="KaP", font=('Quicksand', 16))
        self.KaP_label.grid(row=2, column=0 , padx=5, pady=5,sticky="ew")
        self.KaP_PGbar = ctk.CTkProgressBar(self.LePAsP_frame, progress_color=orange, width=0, height=10)
        self.KaP_PGbar.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        if char.maxKaP == 0:
            self.KaP_PGbar.set(0)
        else:
            self.KaP_PGbar.set(char.KaP/char.maxKaP)
        self.KaP_value = ctk.CTkLabel(self.LePAsP_frame, text="{0:}/{1:}".format(char.KaP, char.maxKaP), font=('Quicksand', 16))
        self.KaP_value.grid(row=2, column=2 , padx=5, pady=5,sticky="ew")

        ### Vorteile & Nachteile
        self.disadvantages = ExpandableFrame(self, "Vor & Nachteile", fg_color="#444444")
        self.disadvantages.grid(row=3, column=0, columnspan=8, padx=5, pady=5, sticky="new")

        self.disadvantages.content.grid_columnconfigure(0, weight=1)
        self.disadvantages.content.grid_columnconfigure(1, weight=1)

        # fill left column
        for i, advantage in enumerate(char.advantages):
            advantage_label = ctk.CTkLabel(self.disadvantages.content, anchor="w", text=advantage, text_color=green_light, font= ("Quicksand", 16))
            advantage_label.grid(row=i+1, column=0, padx=5, pady=1, sticky="new")

        # fill right column
        for i, advantage in enumerate(char.disadvantages):
            advantage_label = ctk.CTkLabel(self.disadvantages.content, anchor="w",  text=advantage, text_color=red_light, font= ("Quicksand", 16))
            advantage_label.grid(row=i+1, column=1, padx=5, pady=1, sticky="new")

        ### Allgemeine Sonderfertigkeiten
        self.special_abilities = ExpandableFrame(self, "Allgemeine Sonderfertigkeiten", fg_color="#444444")
        self.special_abilities.grid(row=4, column=0, columnspan=4, padx=5, pady=5, sticky="new")

        for i, ability in enumerate(char.general_special_abilities):
            sf = ctk.CTkLabel(self.special_abilities.content, anchor="w", text=ability, font= ("Quicksand", 16))
            sf.grid(row=i+1, column=0, padx=5, pady=1, sticky="new")


        ### Kampfsonderfertigkeiten
        self.combat_special_abilities = ExpandableFrame(self, "Kampfsonderfertigkeiten", fg_color="#444444")
        self.combat_special_abilities.grid(row=4, column=4, columnspan=4, padx=5, pady=5, sticky="new")

        for i, ability in enumerate(char.combat_special_abilities):
            sf = ctk.CTkLabel(self.combat_special_abilities.content, anchor="w", text=ability, font= ("Quicksand", 16))
            sf.grid(row=i+1, column=0, padx=5, pady=1, sticky="new")


    def update(self, char):
        if hasattr(self, "init_label"):
            self.create(char)
        else:
            self.name.configure(text=char.name)
            self.MU.configure(text=char.MU)
            self.KL.configure(text=char.KL)
            self.IN.configure(text=char.IN)
            self.CH.configure(text=char.CH)
            self.FF.configure(text=char.FF)
            self.GE.configure(text=char.GE)
            self.KO.configure(text=char.KO)
            self.KK.configure(text=char.KK)

            self.LeP_PGbar.set(char.LeP/char.maxLeP)
            self.LeP_value.configure(text="{0:}/{1:}".format(char.LeP, char.maxLeP))

            if char.maxAsP == 0:
                self.AsP_PGbar.set(0)
            else:
                self.AsP_PGbar.set(char.AsP/char.maxAsP)
            self.AsP_value.configure(text="{0:}/{1:}".format(char.AsP, char.maxAsP))


            if char.maxKaP == 0:
                self.KaP_PGbar.set(0)
            else:
                self.KaP_PGbar.set(char.KaP/char.maxKaP)
            self.KaP_value.configure(text="{0:}/{1:}".format(char.KaP, char.maxKaP))

            for widget in self.disadvantages.content.winfo_children():
                widget.destroy()

            # fill left column
            for i, advantage in enumerate(char.advantages):
                advantage_label = ctk.CTkLabel(self.disadvantages.content, anchor="w", text=advantage, text_color=green_light, font= ("Quicksand", 16))
                advantage_label.grid(row=i+1, column=0, padx=5, pady=1, sticky="new")

            # fill right column
            for i, advantage in enumerate(char.disadvantages):
                advantage_label = ctk.CTkLabel(self.disadvantages.content, anchor="w",  text=advantage, text_color=red_light, font= ("Quicksand", 16))
                advantage_label.grid(row=i+1, column=1, padx=5, pady=1, sticky="new")


            ### Allgemeine Sonderfertigkeiten
            for widget in self.special_abilities.winfo_children():
                widget.destroy()


            for i, ability in enumerate(char.general_special_abilities):
                sf = ctk.CTkLabel(self.special_abilities.content, anchor="w", text=ability, font= ("Quicksand", 16))
                sf.grid(row=i+1, column=0, padx=5, pady=1, sticky="new")

            ### Kampfsonderfertigkeiten
            for widget in self.combat_special_abilities.winfo_children():
                widget.destroy()

            for i, ability in enumerate(char.combat_special_abilities):
                sf = ctk.CTkLabel(self.combat_special_abilities.content, anchor="w", text=ability, font= ("Quicksand", 16))
                sf.grid(row=i+1, column=0, padx=5, pady=1, sticky="new")

# --- Side bar frame class ---
class CharacterList(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.update()

    def update(self):
        for widget in self.winfo_children():
            widget.destroy()

        for i, char in enumerate(self.master.actors):
            # considere handing over the upate and delete_character functions in case the master changes...
            character_info_btn = ctk.CTkButton(self, text=char.name, fg_color=teal, hover_color=teal_light, font= ("Quicksand", 16, "bold"), width=0, command = lambda c=char: self.master.character_detail_frame.update(c))
            character_info_btn.grid(row=i, column=0, sticky="ew", padx=10, pady=(10,0))

            delete_char_btn = ctk.CTkButton(self, text="", image=trash_icon, fg_color=red, hover_color=red_hover,  width=1, command = lambda c=char: self.master.delete_character(c), font= ("Quicksand", 16, "bold"))
            delete_char_btn.grid(row=i, column=1, sticky="e", padx=(0,10), pady=(10, 0))

            # Store references
            char.widgets = {"popup_btn": character_info_btn, "delete_btn": delete_char_btn}

        add_button_frame = ctk.CTkFrame(self, fg_color="#333333")
        add_button_frame.grid(row=i+1, sticky="ew", column=0, columnspan=2)

        add_button_frame.grid_columnconfigure(1, weight=1)
        add_button_frame.grid_columnconfigure(0, weight=0)

        add_button = ctk.CTkButton(add_button_frame, text=plus_icon, text_color="#999999", fg_color="#444444", hover_color="#555555", font= ("Quicksand", 16, "bold"), width=28, command = lambda : AddActeurToplevel(self.master) )
        add_button.grid(row=0, column=0, sticky="w", padx=10, pady=(10,0))

        add_button_label = ctk.CTkLabel(add_button_frame, text="Hinzufügen", text_color="#999999", anchor="w",  width=0, fg_color="#333333", font= ("Quicksand", 16, "italic"))
        add_button_label.grid(row=0, column=1, sticky="ew", padx=(0,10), pady=(10,0))

        bottom_spacer = ctk.CTkFrame(self, height=10, width=2, fg_color="#333333")
        bottom_spacer.grid(row=i+2, column=0, columnspan=2)



class AddActeurToplevel(ctk.CTkToplevel):
    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)

        self.master = master
        self.title("Akteur hinzufügen...")
        for i in range(3):
            self.grid_columnconfigure(i, weight=1)

        mail_label = ctk.CTkLabel(self, text="Füge eine Charakter oder eine Kratur zur Liste der Akteure hinzu...", font=('Quicksand', 22, 'bold'))
        mail_label.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=(10,0))

        from_PDF = ctk.CTkButton(self, text="Charakter PDF", fg_color=teal, hover_color=teal_light, font= ("Quicksand", 16, "bold"), command = self.add_from_PDF)
        from_PDF.grid(row=1, column=0, sticky="ew", padx=10, pady=(10,0))

        creature = ctk.CTkButton(self, text="Kreatur", fg_color=teal, hover_color=teal_light, font= ("Quicksand", 16, "bold"))
        creature.grid(row=1, column=1, sticky="ew", padx=10, pady=(10,0))

        manuel = ctk.CTkButton(self, text="Manuell", fg_color=teal, hover_color=teal_light, font= ("Quicksand", 16, "bold"))
        manuel.grid(row=1, column=2, sticky="ew", padx=10, pady=(10,0))

        close_button = ctk.CTkButton(self, text="Schließen", fg_color=teal, hover_color=teal_light, font= ("Quicksand", 16, "bold"), command=self.destroy)
        close_button.grid(row=2, column=1, padx=10, pady=(10,0))

    def add_from_PDF(self):
        file_path = filedialog.askopenfilename(title="Wähle eine Datei", filetypes=(("PDF files", "*.pdf"), ("All files", "*.*")))
        if file_path:
            self.master.actors.append(Character(file_path))
            self.master.character_frame.update()

class HealToplevel(ctk.CTkToplevel):
    def __init__(self, master, char, **kwargs):
        super().__init__(**kwargs)
        self.master = master
        self.char = char
        self.title("Heile LeP")
        self.grid_columnconfigure(1, weight=1)

        self.mail_label = ctk.CTkLabel(self, text="Um wie viele LeP wird {:} geheilt?".format(char.name), font=('Quicksand', 16))
        self.mail_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10,0))

        self.entry = ctk.CTkEntry(self, font=('Quicksand', 16))
        self.entry.grid(row=0, column=1, sticky="ew", padx=10, pady=(10,0))
        self.entry.bind("<Return>", self.confirm)

    def confirm(self, event=None):
        heal = re.findall(r'-?\d+', self.entry.get())
        if len(heal) != 0:
            self.char.heal(int(heal[0]))
            self.master.LeP_PGbar.set(self.char.LeP/self.char.maxLeP)
            self.master.LeP_value.configure(text='{0:}/{1:}'.format(self.char.LeP, self.char.maxLeP))
            self.destroy()
        else:
            self.destroy()

class DamageToplevel(ctk.CTkToplevel):
    def __init__(self, master, char, **kwargs):
        super().__init__(**kwargs)
        self.master = master
        self.char = char
        self.title("Heile LeP")
        self.grid_columnconfigure(1, weight=1)

        self.mail_label = ctk.CTkLabel(self, text="Wie viel Schaden erleidet {:}?".format(char.name), font=('Quicksand', 16))
        self.mail_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10,0))

        self.entry = ctk.CTkEntry(self, font=('Quicksand', 16))
        self.entry.grid(row=0, column=1, sticky="ew", padx=10, pady=(10,0))
        self.entry.bind("<Return>", self.confirm)

    def confirm(self, event=None):
        dmg = re.findall(r'-?\d+', self.entry.get())
        if len(dmg) != 0:
            self.char.schaden(int(dmg[0]))
            self.master.LeP_PGbar.set(self.char.LeP/self.char.maxLeP)
            self.master.LeP_value.configure(text='{0:}/{1:}'.format(self.char.LeP, self.char.maxLeP))
            self.destroy()
        else:
            self.destroy()



class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("1000x1000") 
        self.title("PnP Session") # Titel des Fensters setzen

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)


        self.actors = []
        # Store button references to manage them dynamically
        for character in os.listdir('characters'):
            char = Character("characters/{:}".format(character), name=re.findall(r'^(\w+)\.pdf$', character)[0])
            self.actors.append(char) 

        # Label of the character list
        #character_list_label = ctk.CTkLabel(self, text="Akteure", fg="white", bg="#1A1D22", font=('Quicksand', 16, 'bold'), height=1, width=10, anchor="center")
        self.character_list_label = ctk.CTkLabel(self, text="Akteure", font=('Quicksand', 22, 'bold'))
        self.character_list_label.grid(row=0, column=0, padx=5, pady=10, sticky="ew")

        self.character_list_label = ctk.CTkLabel(self, text="Informationen", font=('Quicksand', 22, 'bold'))
        self.character_list_label.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        self.character_detail_frame = CharacterFrame(self, fg_color="#333333")
        self.character_detail_frame.grid(row=1, column=1, padx=10, pady=(5, 5), sticky="nsew")

        self.character_frame = CharacterList(self, fg_color="#333333")
        self.character_frame.grid(row=1, column=0, padx=10, pady=(5, 5), sticky="new")

    def delete_character(self, char):
        self.actors.remove(char)
        for widget in char.widgets.values():
            widget.destroy()
        del char

    def heal(self, char):
        pain_index = int(4*(char.maxLeP - char.LeP)/char.maxLeP)
        char.LeP += amount
        if char.LeP > char.maxLeP:
            char.LeP = char.maxLeP
        else:
            if int(4*(char.maxLeP - char.LeP)/char.maxLeP) != pain_index:
                char.statuus['Schmerz'] -= pain_index - int(4*(char.maxLeP - char.LeP)/char.maxLeP) 
                if char.statuus['Schmerz'] == 0:
                    char.statuus.pop('Schmerz')


app = App()
app.mainloop()