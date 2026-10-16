from Role_checks import *
import tkinter as tk
from tkinter import ttk
import os

Klatu_link = 'Klatu3.pdf'
eisgeist_link = 'https://dsa.ulisses-regelwiki.de/Best_Eisgeist.html'
'''
# create characters
Klatu = Character(Klatu_link, name='Klatu')
Adriana = Character(Klatu_link, name='Adriana')
Azir = Character(Klatu_link, name='Azir')

# create a Session
Session = EventTracker(Klatu, Azir, Adriana)

# add effects and events
Session.add_effect('Adriana heult rum', 2)
Session.add_event('Das Tor bricht', 5)

# start an encounter
Session.encounter()
'''


# 1. Hauptfenster erstellen
root = tk.Tk()
root.configure(bg="#1A1D22")
root.geometry("1000x1000") 
root.title("PnP Session") # Titel des Fensters setzen


# Def Styles

button1_img = tk.PhotoImage(file="res/button1.png")
button2_img = tk.PhotoImage(file="res/button2.png")
character_button = button1_img.subsample(2, 4)
character_button_hover = button2_img.subsample(2, 4)

delete_button = button1_img.subsample(7, 4)
delete_button_hover = button2_img.subsample(7, 4)


def create_button(master, text, command=None, **kwargs):
    """Creates a tk.Button with default style, allows overrides via kwargs."""
    defaults = {
        "font": ("Quicksand", 16, "bold"),
        "bg": "#1A1D22",
        "fg": "#99FFFF",
        "activebackground": "#1A1D22",
        "activeforeground": "white",
        "relief": "flat",
        "borderwidth": 0,
        "highlightthickness" : 0,
        "cursor": "hand2",
        "padx": 0,
        "pady": 0,
        "compound" : "center"
    }
    defaults.update(kwargs)  # allow overrides
    return tk.Button(master, text=text, command=command, **defaults)


'''
pack(
    side="top",      # stick to top
    fill="x",        # fill horizontally
    expand=True,     # take up extra space
    padx=10, pady=5, # external padding
    ipadx=5, ipady=5,# internal padding
    anchor="n"       # stick to top within space
)'''

########################################## ACTORS ##########################################
character_frame = tk.Frame(root, bg="#1A1D22")
character_frame.pack(pady=20, fill="both", expand=True)

# Label of the character list
character_list_label = tk.Label(character_frame, text="Akteure", fg="white", bg="#1A1D22", font=('Quicksand', 16, 'bold'), height=1, width=10, anchor="center")
character_list_label.pack(pady=20, anchor="nw")

def character_popup(char):
    popup = tk.Toplevel(root, bg="#1A1D22")
    popup.title("{:}".format(char.name))
    label = tk.Label(popup, text="{:}".format(char.name), fg = "white", font=("Quicksand", 16, 'bold'))
    label.pack(padx=20, pady=20)
    close_button = tk.Button(popup, text="Close", command=popup.destroy)
    close_button.pack(pady=10)

def delete_character(char):
    actors.remove(char)
    for widget in char.widgets.values():
        widget.destroy()
    del char


# create list of actors
actors = []
# Store button references to manage them dynamically
character_widgets = {}  # key = character name, value = dict of widgets
for character in os.listdir('characters'):
    char = Character("characters/{:}".format(character), name=re.findall(r'^(\w+)\.pdf$', character)[0])
    actors.append(char) 

    # Frame to hold buttons for this character
    frame = tk.Frame(character_frame, background="#1A1D22", borderwidth=0)
    frame.pack(pady=5, fill="x")

    character_info_btn = create_button(frame, text=char.name, command = lambda c=char: character_popup(c), image = character_button )
    character_info_btn.bind("<Enter>", lambda e, b=character_info_btn: b.config(image=character_button_hover))
    character_info_btn.bind("<Leave>", lambda e, b=character_info_btn: b.config(image=character_button))
    character_info_btn.pack(side="left", fill="x", padx=0)

    delete_char_btn = create_button(frame, text='X', command = lambda c=char: delete_character(c), fg='red', font= ("Quicksand", 22, "bold"), image = delete_button)
    delete_char_btn.bind("<Enter>", lambda e, b=delete_char_btn: b.config(image=delete_button_hover))
    delete_char_btn.bind("<Leave>", lambda e, b=delete_char_btn: b.config(image=delete_button))
    delete_char_btn.pack(side="left", padx=0)

    # Store references
    char.widgets = {"frame": frame, "popup_btn": character_info_btn, "delete_btn": delete_char_btn}
'''
# dropdown menue showing available character sheets
selected_name = tk.StringVar() 


combo = ttk.Combobox(root, textvariable=selected_name, values=character_PDFs, state="readonly")
combo.grid(row=1, column=0) 

def show_choice(event=None):
    print("Selected:", selected_name.get())

combo.bind("<<ComboboxSelected>>", show_choice)


# Add character
def add_character(event=None):
    name = character_name.get().strip()
    if name:
        actors.append( Character(Klatu_link, name=name) ) 
        character_list.insert(tk.END, name) 
        character_name.set("")
    print('{:} was added!'.format(name))

def on_delete_key(event):
    selected = character_list.curselection()
    if selected:
        index = selected[0]
        Session.delete_actors( character_list.get(index) )
        character_list.delete(index)

# Element erzeugen
# text = '...'      -   text
# image = '...png'  -   bild
# fg = 'color'      -   text farbe
# bg = 'color'      -   text hingergrund farbe
# font=('times', 25, 'bold', 'italic')  -   schriftart, größe, bold, italic
# anchor = n, s, w, e, sw, se, center

label2 = tk.Label(root, text="Effekte", fg="black", font=('Quicksand', 16, 'bold'))
label3 = tk.Label(root, text="Events", fg="black", font=('Quicksand', 16, 'bold'))

# Text zum Fesnter hinzufügen/anzeigen
# side = 'left'/'right'/'top'/'bottom 
#label1.pack(side='left') 

# Text zum Fesnter hinzufügen/anzeigen
# row = int, column = int
# sticky = "n, s, w, e, sw, se, ..“ text ausrichtung
# INFOS
#print(dir(tk.Grid))
#print(help(tk.Grid.grid))
label2.grid(row=1, column=1, sticky="ne") 
label3.grid(row=0, column=2) 


# Create List of Characters
character_list = tk.Listbox(root)
character_list.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
character_list.bind("<Delete>", on_delete_key)

# --- frame at bottom for entry + button ---
bottom_frame = tk.Frame(root)
bottom_frame.grid(row=3, column=0, pady=10)

# Eingabefeld
# Parameter: background, bd, bg, borderwidth, fg, foreground, justify, relief, takefocus, width
character_name=tk.StringVar()
eingabefeld=tk.Entry(bottom_frame, textvariable=character_name)
eingabefeld.pack(side="left", padx=5)
eingabefeld.bind("<Return>", add_character)

#print(character_name.get())
#character_name.set('Adriana')

add_button = tk.Button(bottom_frame, text="Add", cursor='hand2', command = add_character )
add_button.pack(side="left", padx=5)

# Suche nach Radio button für mehr auswahl
'''
# 3. Hauptschleife starten
root.mainloop()
