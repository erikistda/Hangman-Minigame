from importlib import reload
import tkinter as tk
import string
from tkinter import font
from turtle import back
import json
import pygame
import os
import threading

SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "Sounds")

pygame.mixer.init()
# Settings
font_sizes_standard = [14,20,24,28,40,60]
font_sizes_big = [18, 26, 31, 36, 52, 78]
font_sizes_small = [11, 16, 19, 22, 32, 48]
font_size1 = font_sizes_standard[0]
font_size2 = font_sizes_standard[1]
font_size3 = font_sizes_standard[2]
font_size4 = font_sizes_standard[3]
font_size5 = font_sizes_standard[4]
font_size6 = font_sizes_standard[5]
current_font_size = "Standard"

standard_background_clours = ["#869fb3", "#AAC1D2", "#EAE5E3"]
secondary_background_colours = ["#CCFFCC", "#FC8EAC", "#FF7518"]
tertiarty_backgroud_colours = ["#FFA896", "#FFED29", "#B163FF"]
menu_colour = standard_background_clours[0]
game_colour = standard_background_clours[1]
screen_colour = standard_background_clours[2]

game_row_frames = []

# Window setup
def on_escape(event=None):
    root.destroy()
root = tk.Tk() 
root.title("Hangman Minigame")
root.attributes("-fullscreen",True)
root.configure(bg=menu_colour)
root.bind_all("<Escape>",on_escape)
root.resizable(False,False)

#Screens

screen_menu = tk.Frame(root,bg=menu_colour)
screen_game = tk.Frame(root,bg=game_colour)
screen_settings = tk.Frame(root,bg=screen_colour)
screen_highscores = tk.Frame(root,bg=screen_colour)

for frame in (screen_menu,screen_game,screen_settings,screen_highscores):
    frame.place(relwidth=1,relheight=1)

#Zurück Funkrion
def go_back():
    screen_menu.tkraise()

#Menu
# Hangman-Logo im Menü
menu_canvas = tk.Canvas(screen_menu, width=800, height=300, bg=menu_colour, highlightthickness=0)
menu_canvas.pack(pady=50)

# HÄNGE-Text (fett und unterstrichen)
menu_canvas.create_text(
    400, 100,
    text="HÄNGE",
    font=("Arial", font_size6, "bold underline"),
    fill="white"
)

# Position der Unterstreichung unter dem N
x_n = 400 + 55   # leicht angepasst, damit es wirklich am N ist
y_underline = 100 + 40  # etwas unterhalb der Buchstaben

# Seil (weiss)
y_seil_end = 175
menu_canvas.create_line(x_n, y_underline, x_n, y_seil_end, fill="white", width=2)

# Kopf (leicht geneigt, etwas nach rechts)
kopf_radius = 15
menu_canvas.create_oval(
    x_n - kopf_radius + 7,
    y_seil_end + 2,
    x_n + kopf_radius + 3,
    y_seil_end + 2*kopf_radius + 2,
    fill="black"
)

# Körper
körper_länge = 40
menu_canvas.create_line(
    x_n + 3,
    y_seil_end + 2*kopf_radius + 2,
    x_n + 3,
    y_seil_end + 2*kopf_radius + körper_länge + 2,
    fill="black",
    width=2
)

# Arme
menu_canvas.create_line(
    x_n + 3, y_seil_end + 2*kopf_radius + 10,
    x_n - 10, y_seil_end + 2*kopf_radius + 25,
    fill="black", width=2
)
menu_canvas.create_line(
    x_n + 3, y_seil_end + 2*kopf_radius + 10,
    x_n + 16, y_seil_end + 2*kopf_radius + 25,
    fill="black", width=2
)

# Beine
menu_canvas.create_line(
    x_n + 3, y_seil_end + 2*kopf_radius + körper_länge,
    x_n - 10, y_seil_end + 2*kopf_radius + körper_länge + 30,
    fill="black", width=2
)
menu_canvas.create_line(
    x_n + 3, y_seil_end + 2*kopf_radius + körper_länge,
    x_n + 15, y_seil_end + 2*kopf_radius + körper_länge + 30,
    fill="black", width=2
)

btn_spielen=tk.Button(screen_menu,text="PLAY",font=("Arial",font_size2),width=15,
                      command=lambda:screen_game.tkraise())
btn_spielen.pack(pady=10)

btn_einstellungen=tk.Button(screen_menu,text="SETTINGS",font=("Arial",font_size2),width=15,
                      command=lambda:screen_settings.tkraise())
btn_einstellungen.pack(pady=10)

btn_highscores=tk.Button(screen_menu,text="HIGHSCORES",font=("Arial",font_size2),width=15,
                      command=lambda:screen_highscores.tkraise())
btn_highscores.pack(pady=10)

btn_beenden=tk.Button(screen_menu,text="EXIT",font=("Arial",font_size2),width=15,
                      command=root.destroy)
btn_beenden.pack(pady=10)

# PLAY-Screen
import random

# --- Aufbau des Screens ---
screen_game.configure(bg="#AAC1D2")
# Zeichenfläche für Hangman 
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

def update_word_display():
    display = " ".join([c if c in erratene_buchstaben else "_" for c in geheime_wort])
    word_label.config(text=display)


game_back_button = tk.Button(screen_game, text="← BACK", font=("Arial", font_size1), command=go_back)
game_back_button.place(x=20, y=20)
word_label = tk.Label(screen_game, text="", font=("Courier", font_size4), bg="#AAC1D2") # Wortanzeige 
word_label.pack(pady=10)
hearts_label = tk.Label(screen_game, text="", font=("Arial", font_size2), bg="#AAC1D2") # Herzen
hearts_label.pack()
def update_hearts():
    hearts_label.config(text="❤️ " * leben)


# Tastatur 
keyboard_frame = tk.Frame(screen_game, bg="#AAC1D2")
keyboard_frame.pack(side="bottom", pady=50)

keys = {}
letters = list("QWERTZUIOPÜASDFGHJKLÖÄYXCVBNM")
layout = ["QWERTZUIOPÜ", "ASDFGHJKLÖÄ", "YXCVBNM"]

for row in layout:
    row_frame = tk.Frame(keyboard_frame, bg="#AAC1D2")
    row_frame.pack()
    game_row_frames.append(row_frame)
    for char in row:
        lbl = tk.Label(row_frame, text=char, font=("Arial", font_size2), width=4, height=2,
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
        keys[key].config(bg="#9fff9f")
        play_sound_async(SOUND_CORRECT)#update
    else:
        keys[key].config(bg="#ff9f9f")
        play_sound_async(SOUND_WRONG)#update
        leben -= 1
        draw_hangman_stage()
        update_hearts()
    update_word_display()

    # gewonnen oder verloren
    if leben == 0:
        word_label.config(text=f"Verloren! Das Wort war {geheime_wort}")
        play_sound_async(SOUND_LOSE)#update
    elif all(c in erratene_buchstaben for c in geheime_wort):
        word_label.config(text="🎉 Gewonnen!")
        play_sound_async(SOUND_WIN)#update




# Themen mit Wörtern
themen_woerter = {
    "Länder": ["AFGHANISTAN", "ÄGYPTEN", "ALBANIEN", "ALGERIEN", "ARGENTINIEN", "ARMENIEN", "AUSTRALIEN", "ÖSTERREICH", "BANGLADESCH", "BELGIEN", "BOLIVIEN", "BRASILIEN", "BULGARIEN", "KANADA", "CHILE", "CHINA", "KOLUMBIEN", "KROATIEN", "TSCHECHISCHE REPUBLIK", "DÄNEMARK", "DOMINIKANISCHE REPUBLIK", "ECUADOR", "ÄTHIOPIEN", "FINNLAND", "FRANKREICH", "GEORGIEN", "DEUTSCHLAND", "GHANA", "GRIECHENLAND", "GUATEMALA", "HAITI", "HONDURAS", "UNGARN", "ISLAND", "INDIEN", "INDONESIEN", "IRAN", "IRAK", "IRLAND", "ISRAEL", "ITALIEN", "JAPAN", "JORDANIEN", "KENIA", "KOREA, NORD", "KOREA, SÜD", "KUWAIT", "LETTLAND", "LIBANON", "LITAUEN", "LUXEMBURG", "MADAGASKAR", "MALAYSIA", "MALI", "MALTA", "MAURITIUS", "MEXIKO", "MOLDAVIEN", "MONGOLEI", "MONTENEGRO", "MAROKKO", "MOSAMBIK", "MYANMAR", "NAMIBIA", "NEPAL", "NIEDERLANDE", "NEUSEELAND", "NICARAGUA", "NIGERIA", "NORWEGEN", "PAKISTAN", "PANAMA", "PARAGUAY", "PERU", "PHILIPPINEN", "POLEN", "PORTUGAL", "KATAR", "RUMÄNIEN", "RUSSLAND", "SAUDI-ARABIEN", "SENEGAL", "SERBIEN", "SINGAPUR", "SLOWAKEI", "SLOWENIEN", "SÜDAFRIKA", "SPANIEN", "SRI LANKA", "SCHWEDEN", "SCHWEIZ", "SYRIEN", "TAIWAN", "THAILAND", "TUNESIEN", "TÜRKEI", "UKRAINE", "VEREINIGTE ARABISCHE EMIRATE", "VEREINIGTES KÖNIGREICH", "USA", "URUGUAY", "VENEZUELA", "VIETNAM", "ZAMBIA", "ZIMBABWE"],
    "Hauptstädte": ["BERLIN", "PARIS", "LONDON", "ROM", "MADRID", "OTTAWA", "MOSKAU", "PEKING", "TOKIO", "SEOUL", "BRASILIA", "BUENOSAIRES", "MEXIKOSTADT", "CANBERRA", "WIEN", "AMSTERDAM", "BRÜSSEL", "STOCKHOLM", "OSLO", "KOPENHAGEN", "HELSINKI", "WARSCHAU", "PRAG", "BUDAPEST", "ATHEN", "ANKARA", "JERUSALEM", "RIAD", "KAIRO", "BANGKOK", "DELHI", "ISLAMABAD", "JAKARTA", "MANILA", "HANOI", "SINGAPUR", "ABUDHABI", "DOHA", "TEHERAN", "BAGDAD", "DAMASKUS", "KABUL", "RABAT", "ALGIER", "TUNIS", "PRETORIA", "NAIROBI", "VILNIUS", "TALLINN", "BERN"],
    "Tiere": ["HUND", "KATZE", "PFERD", "KUH", "SCHWEIN", "SCHAF", "ZIEGE", "HASE", "KANINCHEN", "HAMSTER", "MAUS", "RATTE", "MEERSCHWEINCHEN", "FUCHS", "WOLF", "BÄR", "LÖWE", "TIGER", "LEOPARD", "GEPARD", "ELEFANT", "NASHORN", "FLUSSPFERD", "AFFE", "GORILLA", "SCHIMPANSE", "ORANGUTAN", "GIRAFFE", "ZEBRA", "KROKODIL", "ALLIGATOR", "SCHILDKRÖTE", "ECHSE", "SCHLANGE", "PYTHON", "KOBRA", "IGEL", "MAULWURF", "REH", "HIRSCH", "ELCH", "WILDSCHWEIN", "DACH", "MARDER", "WIESEL", "OTTER", "SEEHUND", "WALROSS", "DELFIN", "WAL", "HAI", "ROCHEN", "FISCH", "FORELLE", "LACHS", "KARPEN", "HECHT", "STÖR", "SPATZ", "AMSEL", "MEISE", "TAUBE", "ENTE", "GANS", "SCHWAN", "ADLER", "FALKE", "GEIER", "EULE", "PAPAGEI", "WELLENSITTICH", "KANARIE", "HÜHNER", "HAHN", "HENNE", "TRUTHAN", "STRAUSS", "PFAU", "KÄFER", "AMEISE", "BIENE", "WESPE", "FLIEGE", "MÜCKE", "LIBELLE", "SCHMETTERLING", "SPINNE", "SKORPION", "KREBS", "HUMMER", "QUALLE", "SEESTERN", "SEEPFERDCHEN", "OCTOPUS", "TINTENFISCH", "MUSCHEL", "SCHNECKE", "ALPAKA", "LAMA", "YAK", "REGENWURM"],
    "Informatik": ["ALGORITHMUS", "ANWENDUNG", "ARRAY", "ARBEITSSPEICHER", "BACKEND", "BROWSER", "CACHE", "CLOUD", "CODE", "COMPUTER", "CPU", "DATEN", "DATENBANK", "DEBUGGING", "DEKODIERUNG", "DESIGN", "DIGITAL", "DOMAIN", "DOWNLOAD", "EINGABE", "ENCRYPTION", "ETHERNET", "FESTPLATTE", "FIREWALL", "FIRMWARE", "FORMAT", "FRAMEWORK", "FUNKTION", "GATEWAY", "GRAFIK", "HARDWARE", "HOSTING", "INDEX", "INFRASTRUKTUR", "INPUT", "INSTALLATION", "INTERNET", "IPADRESSE", "JAVA", "JAVASCRIPT", "KERNEL", "KEYBOARD", "KOMPILER", "KONFIGURATION", "KONTROLLE", "LAPTOP", "LINUX", "LOGIN", "LOGIK", "MAINFRAME", "MAINBOARD", "MALWARE", "MEMORY", "MODEM", "MONITOR", "NETZWERK", "OBJEKT", "OPENSOURCE", "OPTIMIERUNG", "OUTPUT", "PAKET", "PASSWORT", "PATCH", "PIXEL", "PLATTFORM", "PORTAL", "PROTOKOLL", "PROZESS", "PROZESSOR", "PROGRAMM", "PROGRAMMIERUNG", "RECHNER", "RECHTE", "ROUTER", "SCRIPT", "SERVER", "SOFTWARE", "SOURCECODE", "SPEICHER", "STRUKTUR", "SYNTAX", "SYSTEM", "TABLET", "TERMINAL", "TOOL", "UPLOAD", "URLADRESSE", "USERID", "VARIABLE", "VIRUS", "VIRTUALISIERUNG", "VPN", "WEBSITE", "WINDOWS", "WORKFLOW", "ZUGRIFF", "ZERTIFIKAT", "ZUSAMMENFÜHRUNG", "ZUWEISUNG", "ZWISCHENSPEICHER"],
    "Elemente": ["WASSER", "FEUER", "ERDE", "LUFT", "BLITZ", "STURM", "REGEN", "NEBEL", "WOLKE", "WIND", "EISEN", "HOLZ", "STEIN", "SAND", "SCHNEE", "GLUT", "FLAMME", "ASCHE", "RAUCH", "GEWITTER", "DONNER", "HAGEL", "FLUSS", "SEELE", "ENERGIE", "MAGMA", "LAVA", "KRISTALL", "METALL", "PLASMA", "ATOM", "MOLEKÜL", "SAUERSTOFF", "KOHLENSTOFF", "STICKSTOFF", "WASSERSTOFF", "HELION", "NEUTRON", "ELEKTRON", "PROTON", "IONEN", "QUARZ", "SALZ", "KALK", "MINERAL", "ERZ", "ÖL", "BENZIN", "GAS", "DAMPF", "DRUCK", "TEMPERATUR", "LICHT", "SCHATTEN", "FUNKEN", "WÄRME", "KÄLTE", "VULKAN", "ERDBEBEN", "TSUNAMI", "GEYSIR", "GEWÄSSER", "ATMOSPHÄRE", "STRÖMUNG", "WELLEN", "TIEFE", "HÖHE", "SCHWERE", "GRAVITATION", "MAGNETISMUS", "ELEKTRIZITÄT", "FELD", "POL", "NORDEN", "SÜDEN", "OSTEN", "WESTEN", "HORIZONT", "SPHÄRE", "DIMENSION", "ZEIT", "RAUM", "KONTINENT", "OZEAN", "MEER", "INSEL", "BERG", "TAL", "HÖHLE", "KLIMA", "ZONEN", "TROPFEN", "QUELLE", "STROM", "BACH", "WURZEL", "BLATT", "AST", "STIEL", "KRONE", "STAMM"],
    "Dinosaurier": ["TYRANNOSAURUS", "TRICERATOPS", "VELOCIRAPTOR", "STEGOSAURUS", "BRACHIOSAURUS", "ALLOSAURUS", "SPINOSAURUS", "ANKYLOSAURUS", "IGUANODON", "DIPLODOCUS", "APATOSAURUS", "PACHYCEPHALOSAURUS", "CARNOTAURUS", "GIGANOTOSAURUS", "MEGALOSAURUS", "DEINONYCHUS", "MAIASAURA", "PARASAUROLOPHUS", "SAUROLOPHUS", "CORYTHOSAURUS", "EDMONTOSAURUS", "LAMBEOSAURUS", "OURANOSAURUS", "THERIZINOSAURUS", "MICRORAPTOR", "ARCHAEOPTERYX", "TROODON", "ORNITHOMIMUS", "STRUTHIOMIMUS", "DRACOREX", "STYRACOSAURUS", "PENTACERATOPS", "PROTOCERATOPS", "PSITTACOSAURUS", "HYPSILOPHODON", "LEAELLYNASAURA", "MUTTABURRASAURUS", "TENONTOSAURUS", "CERATOSAURUS", "COELOPHYSIS", "HERRERASAURUS", "PLATEOSAURUS", "MASSOSPONDYLUS", "RIOJASAURUS", "SHUNOSAURUS", "JOBARIA", "NIGERSAURUS", "TARBOSAURUS", "MONOLOPHOSAURUS", "MAJUNGASAURUS"]
}

kategorie_index = 0
auswahl_aktiv = True
geheime_wort = ""
erratene_buchstaben = set()
leben = 6
hangman_parts = []


# Frame für Auswahl
auswahl_frame = tk.Frame(screen_game, bg="#AAC1D2")
auswahl_frame.pack(expand=True)
auswahl_frame.place(relx=0.5, rely=0.55, anchor="center")


kategorien = list(themen_woerter.keys())

btn_links = tk.Label(auswahl_frame, text="◀", font=("Arial", font_size5), bg="#AAC1D2", cursor="hand2")
btn_links.grid(row=0, column=0, padx=40)

auswahl_label = tk.Label(auswahl_frame, text=kategorien[kategorie_index],
                         font=("Arial", 30, "bold"), width=15, height=2,
                         bg="white", relief="raised", borderwidth=3, cursor="hand2")
auswahl_label.grid(row=0, column=1)

btn_rechts = tk.Label(auswahl_frame, text="▶", font=("Arial", font_size5), bg="#AAC1D2", cursor="hand2")
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


# --SETTINGS-Screen--
settings_label = tk.Label(screen_settings, text="Einstellungen", font=("Arial", font_size3), bg=screen_colour)
settings_label.pack(pady=50)
settings_back_button = tk.Button(screen_settings, text="← BACK", font=("Arial", font_size1), command=go_back)
settings_back_button.place(x=20, y=20)

# Size Controll
def change_text_size():
    global font_size1, font_size2, font_size3, font_size4, font_size5, font_size6, font_sizes_small, font_sizes_standard, font_sizes_big, current_font_size
    if current_font_size == "Standard":
        font_size1 = font_sizes_big[0]
        font_size2 = font_sizes_big[1]
        font_size3 = font_sizes_big[2]
        font_size4 = font_sizes_big[3]
        font_size5 = font_sizes_big[4]
        font_size6 = font_sizes_big[5]
        current_font_size = "Big"
    elif current_font_size == "Big":
        font_size1 = font_sizes_small[0]
        font_size2 = font_sizes_small[1]
        font_size3 = font_sizes_small[2]
        font_size4 = font_sizes_small[3]
        font_size5 = font_sizes_small[4]
        font_size6 = font_sizes_small[5]
        current_font_size = "Small"
    elif current_font_size == "Small":
        font_size1 = font_sizes_standard[0]
        font_size2 = font_sizes_standard[1]
        font_size3 = font_sizes_standard[2]
        font_size4 = font_sizes_standard[3]
        font_size5 = font_sizes_standard[4]
        font_size6 = font_sizes_standard[5]
        current_font_size = "Standard"


    # Settings - Settings Screen
    settings_label.config(font=("Arial", font_size3))
    settings_back_button.config(font=("Arial", font_size1))
    size_button.config(text=current_font_size, font=("Arial", font_size3))
    size_button_identifier.config(font=("Arial", font_size2))
    
    #Settings - Highscore Screen
    highscore_label.config(font=("Arial", font_size3))
    highscore_back_button.config(font=("Arial", font_size1))

    # Settings - Game Screen
    game_back_button.config(font=("Arial", font_size1))
    word_label.config(font=("Courier", font_size4))
    hearts_label.config(font=("Arial", font_size2))
    
    # Settings - Menu Screen
    btn_spielen.config(font=("Arial", font_size2))
    btn_einstellungen.config(font=("Arial", font_size2))
    btn_highscores.config(font=("Arial", font_size2))
    btn_beenden.config(font=("Arial", font_size2))

    # Settings - Game Screen Auswahl Frame
    btn_links.config(font=("Arial", font_size5))
    auswahl_label.config(font=("Arial", font_size3, "bold"))
    btn_rechts.config(font=("Arial", font_size5))
    
    # Settings - Game Screen Keyboard (als Schleife)
    for key_label in keys.values():
        key_label.config(font=("Arial", font_size2))



size_control_frame = tk.Frame(screen_settings, bg=screen_colour) 
size_control_frame.pack(pady=20) 
size_button_identifier = tk.Label(size_control_frame, text="Text size", font=("Arial", font_size2), bg=screen_colour)
size_button_identifier.pack(side="left", padx=10)
size_button = tk.Button(size_control_frame, text=current_font_size, font=("Arial", font_size3), command=change_text_size)
size_button.pack(side="left", padx=10)
root.bind("<BackSpace>", lambda event: go_back())


# Background Clolour Controll
def all_redos():
    global screen_colour, menu_colour, game_colour, standard_background_clours, canvas
    # Other Screens
    screen_settings.config(bg=screen_colour)
    screen_highscores.config(bg=screen_colour)
    size_button_identifier.config(bg=screen_colour)
    settings_label.config(bg=screen_colour)
    size_control_frame.config(bg=screen_colour)
    background_control_frame1.config(bg=screen_colour)
    highscore_label.config(bg=screen_colour)
    background_control_frame2.config(bg=screen_colour)
    background_control_frame3.config(bg=screen_colour)
    background_titel1.config(bg=screen_colour)
    background_titel2.config(bg=screen_colour)
    background_titel3.config(bg=screen_colour)
    # Menu Screen
    screen_menu.config(bg=menu_colour)
    menu_canvas.config(bg=menu_colour)
    # Game Screen
    screen_game.config(bg=game_colour)
    word_label.config(bg=game_colour)
    hearts_label.config(bg=game_colour)
    auswahl_frame.config(bg=game_colour)
    btn_links.config(bg=game_colour)
    btn_rechts.config(bg=game_colour)
    canvas.config(bg=game_colour)
    keyboard_frame.config(bg=game_colour) #keyboard 
    for frame in game_row_frames: 
        frame.config(bg=game_colour) 
    
def background_screen_change1():
    global screen_colour, standard_background_clours
    if screen_colour == standard_background_clours[2]:
        pass
    else:
        screen_colour = standard_background_clours[2]
    all_redos()
def background_screen_change2():
    global screen_colour, secondary_background_clours
    if screen_colour == secondary_background_colours[0]:
        pass
    else:
        screen_colour = secondary_background_colours[0]
    all_redos()
def background_screen_change3():
    global screen_colour, tertiarty_backgroud_colours
    if screen_colour == tertiarty_backgroud_colours[0]:
        pass
    else:
        screen_colour = tertiarty_backgroud_colours[0]
    all_redos()
def background_game_change1():
    global game_colour, standard_background_clours
    if game_colour == standard_background_clours[1]:
        pass
    else:
        game_colour = standard_background_clours[1]
    all_redos()
def background_game_change2():
    global game_colour, secondary_background_clours
    if game_colour == secondary_background_colours[1]:
        pass
    else:
        game_colour = secondary_background_colours[1]
    all_redos()
def background_game_change3():
    global game_colour, tertiarty_backgroud_colours
    if game_colour == tertiarty_backgroud_colours[1]:
        pass
    else:
        game_colour = tertiarty_backgroud_colours[1]
    all_redos()
def background_menu_change1():
    global menu_colour, standard_background_clours
    if menu_colour == standard_background_clours[0]:
        pass
    else:
        menu_colour = standard_background_clours[0]
    all_redos()
def background_menu_change2():
    global menu_colour, secondary_background_clours
    if menu_colour == secondary_background_colours[2]:
        pass
    else:
        menu_colour = secondary_background_colours[2]
    all_redos()
def background_menu_change3():
    global menu_colour, tertiarty_backgroud_colours
    if menu_colour == tertiarty_backgroud_colours[2]:
        pass
    else:
        menu_colour = tertiarty_backgroud_colours[2]
    all_redos()

background_titel1 = tk.Label(screen_settings, text="Background Colour for other Screen's", font=("Arial", font_size2), bg=screen_colour) # Screen Background
background_titel1.pack(pady=20) 
background_control_frame1 = tk.Frame(screen_settings, bg=screen_colour) 
background_control_frame1.pack(pady=30) 
background_change_standard = tk.Button(background_control_frame1, text="Background", font=("Arial", font_size3), bg=standard_background_clours[2], fg=standard_background_clours[2], relief="solid", borderwidth=1.5, command=background_screen_change1)
background_change_standard.pack(side="left", padx=10)
background_change_standard = tk.Button(background_control_frame1, text="Background", font=("Arial", font_size3), bg=secondary_background_colours[0], fg=secondary_background_colours[0], relief="solid", borderwidth=1.5, command=background_screen_change2)
background_change_standard.pack(side="left", padx=10)
background_change_standard = tk.Button(background_control_frame1, text="Background", font=("Arial", font_size3), bg=tertiarty_backgroud_colours[0], fg=tertiarty_backgroud_colours[0], relief="solid", borderwidth=1.5, command=background_screen_change3)
background_change_standard.pack(side="left", padx=10)

background_titel2 = tk.Label(screen_settings, text="Background Colour for the Game", font=("Arial", font_size2), bg=screen_colour)
background_titel2.pack(pady=00)
background_control_frame2 = tk.Frame(screen_settings, bg=screen_colour) # Game Background
background_control_frame2.pack(pady=30) 
background_change_standard = tk.Button(background_control_frame2, text="Background", font=("Arial", font_size3), bg=standard_background_clours[1], fg=standard_background_clours[1], relief="solid", borderwidth=1.5, command=background_game_change1)
background_change_standard.pack(side="left", padx=10)
background_change_standard = tk.Button(background_control_frame2, text="Background", font=("Arial", font_size3), bg=secondary_background_colours[1], fg=secondary_background_colours[1], relief="solid", borderwidth=1.5, command=background_game_change2)
background_change_standard.pack(side="left", padx=10)
background_change_standard = tk.Button(background_control_frame2, text="Background", font=("Arial", font_size3), bg=tertiarty_backgroud_colours[1], fg=tertiarty_backgroud_colours[1], relief="solid", borderwidth=1.5, command=background_game_change3)
background_change_standard.pack(side="left", padx=10)

background_titel3 = tk.Label(screen_settings, text="Background Colour for the Menu", font=("Arial", font_size2), bg=screen_colour)
background_titel3.pack(pady=00)
background_control_frame3 = tk.Frame(screen_settings, bg=screen_colour) # Game Background
background_control_frame3.pack(pady=30) 
background_change_standard = tk.Button(background_control_frame3, text="Background", font=("Arial", font_size3), bg=standard_background_clours[0], fg=standard_background_clours[0], relief="solid", borderwidth=1.5, command=background_menu_change1)
background_change_standard.pack(side="left", padx=10)
background_change_standard = tk.Button(background_control_frame3, text="Background", font=("Arial", font_size3), bg=secondary_background_colours[2], fg=secondary_background_colours[2], relief="solid", borderwidth=1.5, command=background_menu_change2)
background_change_standard.pack(side="left", padx=10)
background_change_standard = tk.Button(background_control_frame3, text="Background", font=("Arial", font_size3), bg=tertiarty_backgroud_colours[2], fg=tertiarty_backgroud_colours[2], relief="solid", borderwidth=1.5, command=background_menu_change3)
background_change_standard.pack(side="left", padx=10)





# Highscore-Screen
highscore_label = tk.Label(screen_highscores, text="Highscores", font=("Arial", font_size3), bg="#EAE5E3")
highscore_label.pack(pady=200)
highscore_back_button = tk.Button(screen_highscores, text="← BACK", font=("Arial", font_size1), command=go_back)
highscore_back_button.place(x=20, y=20)
root.bind("<BackSpace>", lambda event: go_back())

# -----------------------
# Hilfsfunktionen: Sound
# -----------------------

import winsound
import time


def play_sound_async(sound):#update
    threading.Thread(target=play_sound, args=(sound,), daemon=True).start() #update

# Angepasste load_sound-Funktion
def load_sound(name):
    """
    Gibt ein Dictionary zurück, das die Frequenz(en) und Dauer(n) des Sounds enthält.
    """
    if name == "success.wav":  # Win-Sound
        return {"freq": [880], "dur": [300]}
    elif name == "failed.wav":  # Fehler-Sound
        return {"freq": [220], "dur": [300]}
    elif name == "win.wav":     # Sieg-Melodie (kurze Melodie)
        return {"freq": [660, 880, 1320], "dur": [150, 150, 150]}
    elif name == "lost.wav":    # Game Over Sound
        return {"freq": [330, 220], "dur": [300, 300]}
    else:
        return None

# Sounds laden
SOUND_CORRECT = load_sound("success.wav")
SOUND_WRONG   = load_sound("failed.wav")
SOUND_WIN     = load_sound("win.wav")
SOUND_LOSE    = load_sound("lost.wav")

# Abspiel-Funktion
def play_sound(sound):
    if not sound:
        return
    try:
        for f, d in zip(sound["freq"], sound["dur"]):
            winsound.Beep(f, d)
            time.sleep(0.05)  # Kurze Pause zwischen den Tönen
    except Exception as e:
        print("Play sound error:", e)

# Test
if __name__ == "__main__":
    play_sound(SOUND_CORRECT)
    time.sleep(0.4)
    play_sound(SOUND_WRONG)
    time.sleep(0.4)
    play_sound(SOUND_WIN)
    time.sleep(1)
    play_sound(SOUND_LOSE)



# Start mit Menü
screen_menu.tkraise()
root.mainloop()



