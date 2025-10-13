import tkinter as tk
import string

# Window setup
def on_escape(event=None):
    root.destroy()
root = tk.Tk()
root.title("Hangman Minigame")
root.attributes("-fullscreen",True)
root.configure(bg="#869fb3")
root.bind_all("<Escape>",on_escape)
root.resizable(False,False)

#Screens

screen_menu = tk.Frame(root,bg="#869fb3")
screen_game = tk.Frame(root,bg="#AAC1D2")
screen_settings = tk.Frame(root,bg="#EAE5E3")
screen_highscores = tk.Frame(root,bg="#EAE5E3")

for frame in (screen_menu,screen_game,screen_settings,screen_highscores):
    frame.place(relwidth=1,relheight=1)

#Zurück Funkrion

def go_back():
    screen_menu.tkraise()

#Menu
# Hangman-Logo im Menü
canvas = tk.Canvas(screen_menu, width=800, height=300, bg="#869fb3", highlightthickness=0)
canvas.pack(pady=50)

# HÄNGE-Text (fett und unterstrichen)
canvas.create_text(
    400, 100,
    text="HÄNGE",
    font=("Arial", 60, "bold underline"),
    fill="white"
)

# Position der Unterstreichung unter dem N
x_n = 400 + 55   # leicht angepasst, damit es wirklich am N ist
y_underline = 100 + 40  # etwas unterhalb der Buchstaben

# Seil (weiss)
y_seil_end = 175
canvas.create_line(x_n, y_underline, x_n, y_seil_end, fill="white", width=2)

# Kopf (leicht geneigt, etwas nach rechts)
kopf_radius = 15
canvas.create_oval(
    x_n - kopf_radius + 7,
    y_seil_end + 2,
    x_n + kopf_radius + 3,
    y_seil_end + 2*kopf_radius + 2,
    fill="black"
)

# Körper
körper_länge = 40
canvas.create_line(
    x_n + 3,
    y_seil_end + 2*kopf_radius + 2,
    x_n + 3,
    y_seil_end + 2*kopf_radius + körper_länge + 2,
    fill="black",
    width=2
)

# Arme
canvas.create_line(
    x_n + 3, y_seil_end + 2*kopf_radius + 10,
    x_n - 10, y_seil_end + 2*kopf_radius + 25,
    fill="black", width=2
)
canvas.create_line(
    x_n + 3, y_seil_end + 2*kopf_radius + 10,
    x_n + 16, y_seil_end + 2*kopf_radius + 25,
    fill="black", width=2
)

# Beine
canvas.create_line(
    x_n + 3, y_seil_end + 2*kopf_radius + körper_länge,
    x_n - 10, y_seil_end + 2*kopf_radius + körper_länge + 30,
    fill="black", width=2
)
canvas.create_line(
    x_n + 3, y_seil_end + 2*kopf_radius + körper_länge,
    x_n + 15, y_seil_end + 2*kopf_radius + körper_länge + 30,
    fill="black", width=2
)


btn_spielen=tk.Button(screen_menu,text="PLAY",font=("Arial",20),width=15,
                      command=lambda:screen_game.tkraise())
btn_spielen.pack(pady=10)

btn_einstellungen=tk.Button(screen_menu,text="SETTINGS",font=("Arial",20),width=15,
                      command=lambda:screen_settings.tkraise())
btn_einstellungen.pack(pady=10)

btn_highscores=tk.Button(screen_menu,text="HIGHSCORES",font=("Arial",20),width=15,
                      command=lambda:screen_highscores.tkraise())
btn_highscores.pack(pady=10)

btn_beenden=tk.Button(screen_menu,text="EXIT",font=("Arial",20),width=15,
                      command=root.destroy)
btn_beenden.pack(pady=10)

# PLAY-Screen
import random

# Themen mit Wörtern
themen_woerter = {
    "Länder": ["SCHWEIZ", "ITALIEN", "FRANKREICH", "DEUTSCHLAND"],
    "Hauptstädte": ["BERN", "PARIS", "ROM", "BERLIN"],
    "Tiere": ["KATZE", "HUND", "ELEFANT", "LÖWE"],
    "Informatik": ["PYTHON", "ALGORITHMUS", "DATENBANK", "SOFTWARE"],
    "Elemente": ["WASSER", "FEUER", "ERDE", "LUFT"],
    "Dinosaurier": ["CARNOTAURUS", "TREX", "VELOCIRAPTOR", "STEGOSAURUS"]
}

kategorie_index = 0
auswahl_aktiv = True
geheime_wort = ""
erratene_buchstaben = set()
leben = 6
hangman_parts = []

# --- Aufbau des Screens ---
screen_game.configure(bg="#AAC1D2")

# Frame für Auswahl
auswahl_frame = tk.Frame(screen_game, bg="#AAC1D2")
auswahl_frame.pack(expand=True)
auswahl_frame.place(relx=0.5, rely=0.55, anchor="center")


kategorien = list(themen_woerter.keys())

btn_links = tk.Label(auswahl_frame, text="◀", font=("Arial", 40), bg="#AAC1D2", cursor="hand2")
btn_links.grid(row=0, column=0, padx=40)

auswahl_label = tk.Label(auswahl_frame, text=kategorien[kategorie_index],
                         font=("Arial", 30, "bold"), width=15, height=2,
                         bg="white", relief="raised", borderwidth=3, cursor="hand2")
auswahl_label.grid(row=0, column=1)

btn_rechts = tk.Label(auswahl_frame, text="▶", font=("Arial", 40), bg="#AAC1D2", cursor="hand2")
btn_rechts.grid(row=0, column=2, padx=40)

# --- Funktionen ---
def update_kategorie():
    auswahl_label.config(text=kategorien[kategorie_index])

def next_kategorie(event=None):
    global kategorie_index
    if not auswahl_aktiv: return
    kategorie_index = (kategorie_index + 1) % len(kategorien)
    update_kategorie()

def prev_kategorie(event=None):
    global kategorie_index
    if not auswahl_aktiv: return
    kategorie_index = (kategorie_index - 1) % len(kategorien)
    update_kategorie()

# --- Spiel starten ---
def start_game(event=None):
    global geheime_wort, erratene_buchstaben, leben, auswahl_aktiv
    auswahl_aktiv = False
    auswahl_frame.pack_forget()
    geheime_wort = random.choice(themen_woerter[kategorien[kategorie_index]])
    erratene_buchstaben = set()
    leben = 6
    update_word_display()
    draw_gallows()
    update_hearts()

# --- Zeichenfläche für Hangman ---
canvas = tk.Canvas(screen_game, width=400, height=300, bg="#AAC1D2", highlightthickness=0)
canvas.pack(pady=20)

def draw_gallows():
    canvas.delete("all")
    # Gerüst
    canvas.create_line(100, 250, 300, 250, width=4)
    canvas.create_line(150, 250, 150, 50, width=4)
    canvas.create_line(150, 50, 250, 50, width=4)
    canvas.create_line(250, 50, 250, 80, width=3)  # Seil

def draw_hangman_stage():
    parts = [
        lambda: canvas.create_oval(235, 80, 265, 110, width=3),  # Kopf
        lambda: canvas.create_line(250, 110, 250, 160, width=3), # Körper
        lambda: canvas.create_line(250, 120, 230, 140, width=3), # linker Arm
        lambda: canvas.create_line(250, 120, 270, 140, width=3), # rechter Arm
        lambda: canvas.create_line(250, 160, 230, 190, width=3), # linkes Bein
        lambda: canvas.create_line(250, 160, 270, 190, width=3)  # rechtes Bein
    ]
    index = 6 - leben - 1
    if 0 <= index < len(parts):
        parts[index]()

# --- Wortanzeige ---
word_label = tk.Label(screen_game, text="", font=("Courier", 28), bg="#AAC1D2")
word_label.pack(pady=10)

def update_word_display():
    display = " ".join([c if c in erratene_buchstaben else "_" for c in geheime_wort])
    word_label.config(text=display)

# --- Herzen ---
hearts_label = tk.Label(screen_game, text="", font=("Arial", 20), bg="#AAC1D2")
hearts_label.pack()

def update_hearts():
    hearts_label.config(text="❤️ " * leben)

# --- Tastatur ---
keyboard_frame = tk.Frame(screen_game, bg="#AAC1D2")
keyboard_frame.pack(side="bottom", pady=50)

keys = {}
letters = list("QWERTZUIOPÜASDFGHJKLÖÄYXCVBNM")
layout = ["QWERTZUIOPÜ", "ASDFGHJKLÖÄ", "YXCVBNM"]

for row in layout:
    row_frame = tk.Frame(keyboard_frame, bg="#AAC1D2")
    row_frame.pack()
    for char in row:
        lbl = tk.Label(row_frame, text=char, font=("Arial", 20), width=4, height=2,
                       bg="white", relief="raised", borderwidth=2)
        lbl.pack(side="left", padx=3, pady=3)
        keys[char] = lbl

def check_letter(key):
    global leben
    if not geheime_wort or leben <= 0:
        return
    if key in erratene_buchstaben:
        return
    erratene_buchstaben.add(key)

    if key in geheime_wort:
        keys[key].config(bg="#9fff9f")  # richtig = grünlich
    else:
        keys[key].config(bg="#ff9f9f")  # falsch = rot
        leben -= 1
        draw_hangman_stage()
        update_hearts()

    update_word_display()

    # gewonnen oder verloren
    if leben == 0:
        word_label.config(text=f"Verloren! Das Wort war {geheime_wort}")
    elif all(c in erratene_buchstaben for c in geheime_wort):
        word_label.config(text="🎉 Gewonnen!")

# --- Tastatursteuerung ---
umlaut_map = {"adiaeresis": "Ä", "odiaeresis": "Ö", "udiaeresis": "Ü"}

def on_key_press(event):
    if auswahl_aktiv:  # deaktiviert, wenn Thema nicht gewählt
        return
    key = event.keysym.upper()
    if key.lower() in umlaut_map:
        key = umlaut_map[key.lower()]
    if key in keys:
        check_letter(key)

root.bind("<KeyPress>", on_key_press)

# Maus und Tastatur Navigation für Menü
btn_links.bind("<Button-1>", prev_kategorie)
btn_rechts.bind("<Button-1>", next_kategorie)
auswahl_label.bind("<Button-1>", start_game)
root.bind("<Left>", prev_kategorie)
root.bind("<Right>", next_kategorie)
root.bind("<Return>", start_game)

# Zurück-Button
tk.Button(screen_game, text="← BACK", font=("Arial", 14),
          command=go_back).place(x=20, y=20)





# SETTINGS-Screen
tk.Label(screen_settings, text="Einstellungen", font=("Arial", 24), bg="#EAE5E3").pack(pady=200)
tk.Button(screen_settings, text="← BACK", font=("Arial", 14),
          command=go_back).place(x=20, y=20)
root.bind("<BackSpace>", lambda event: go_back())



# Highscore-Screen
tk.Label(screen_highscores, text="Highscores", font=("Arial", 24), bg="#EAE5E3").pack(pady=200)
tk.Button(screen_highscores, text="← BACK", font=("Arial", 14),
          command=go_back).place(x=20, y=20)
root.bind("<BackSpace>", lambda event: go_back())



# Start mit Menü
screen_menu.tkraise()
root.mainloop()