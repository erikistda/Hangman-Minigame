from importlib import reload
import tkinter as tk
import string
import json
import pygame
import os
import threading
import time
import winsound
from tkinter import font
from tkinter import messagebox

SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "Sounds")

pygame.mixer.init()
# --Settings--
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
erster_loesch_knopf = False
anzahl_loesch_knöpfe = 0

# ---Window setup---
def on_escape(event=None):
    root.destroy()
root = tk.Tk() 
root.title("Hangman Minigame")
root.attributes("-fullscreen",True)
root.configure(bg=menu_colour)
root.bind_all("<Escape>",on_escape)
root.resizable(False,False)

#--Screens--
screen_menu = tk.Frame(root,bg=menu_colour)
screen_game = tk.Frame(root,bg=game_colour)
screen_settings = tk.Frame(root,bg=screen_colour)
screen_highscores = tk.Frame(root,bg=screen_colour)

for frame in (screen_menu,screen_game,screen_settings,screen_highscores):
    frame.place(relwidth=1,relheight=1)

#--Zurück Funktion--
def go_back():
    global auswahl_aktiv,leben
    
    # -1. Timer stoppen und ausblenden-
    stop_timer() 
    timer_label.place_forget()
    hide_endgame_buttons()
    
    # -2. Spielzustand zurücksetzen und Auswahl wiederherstellen-
    auswahl_frame.place(relx=0.5, rely=0.55, anchor="center") 
    auswahl_aktiv = True 
    leben = 6
    update_hearts()
    word_label.config(text="")
    canvas.delete("all")
    
    # -3. Oberfläche aufräumen-
    reset_keyboard()
    
    # -Zurück zum Hauptmenü-
    screen_menu.tkraise()

    # Nach Rückkehr ins Menü: alte Pfeiltasten-Bindings wiederherstellen
    root.unbind("<Left>")
    root.unbind("<Right>")
    root.bind("<Left>", prev_kategorie)
    root.bind("<Right>", next_kategorie)

def show_selection():
    global auswahl_aktiv, leben

    # -1. Vorheriges Spiel aufräumen-
    hide_endgame_buttons()
    btn_retry.place_forget() 
    reset_keyboard() 
    leben = 6
    update_hearts() 
    word_label.config(text="")
    hearts_label.pack_forget()
    canvas.delete("all")
    
    # -2. Auswahl-Frame platzieren und Zustand setzen-
    auswahl_frame.place(relx=0.5, rely=0.55, anchor="center")
    auswahl_aktiv = True
    
    # -3. Zum Spielbildschirm wechseln-
    screen_game.tkraise()

#---Menu---
# -Hangman-Logo im Menü-
menu_canvas = tk.Canvas(screen_menu, width=800, height=300, bg=menu_colour, highlightthickness=0)
menu_canvas.pack(pady=50)

# -HÄNGE-Text (fett und unterstrichen)-
menu_canvas.create_text(
    400, 100,
    text="HÄNGE",
    font=("Arial", font_size6, "bold underline"),
    fill="white"
)

# -Position der Unterstreichung unter dem N-
x_n = 400 + 55   # leicht angepasst, damit es wirklich am N ist
y_underline = 100 + 40  # etwas unterhalb der Buchstaben

# -Seil-
y_seil_end = 175
menu_canvas.create_line(x_n, y_underline, x_n, y_seil_end, fill="white", width=2)

# --Kopf--
kopf_radius = 15
menu_canvas.create_oval(
    x_n - kopf_radius + 7,
    y_seil_end + 2,
    x_n + kopf_radius + 3,
    y_seil_end + 2*kopf_radius + 2,
    fill="black"
)

# --Körper--
körper_länge = 40
menu_canvas.create_line(
    x_n + 3,
    y_seil_end + 2*kopf_radius + 2,
    x_n + 3,
    y_seil_end + 2*kopf_radius + körper_länge + 2,
    fill="black",
    width=2
)

# --Arme--
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

# --Beine--
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
                      command=show_selection)
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

# ----PLAY-Screen----
import random

# ---Aufbau des Screens---
screen_game.configure(bg="#AAC1D2")
# -Zeichenfläche für Hangman-
canvas = tk.Canvas(screen_game, width=400, height=300, bg="#AAC1D2", highlightthickness=0)
canvas.pack(pady=20)

def draw_gallows():
    canvas.delete("all")
    # -Gerüst-
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
    display = " ".join([
        c if (c in erratene_buchstaben or c in [" ", "-", ","]) else "_"
        for c in geheime_wort
    ])
    word_label.config(text=display)


game_back_button = tk.Button(screen_game, text="← BACK", font=("Arial", font_size1), command=go_back)
game_back_button.place(x=20, y=20)
word_label = tk.Label(screen_game, text="", font=("Courier", font_size4), bg="#AAC1D2") # Wortanzeige 
word_label.pack(pady=10)
hearts_label = tk.Label(screen_game, text="", font=("Arial", font_size2), bg="#AAC1D2") # Herzen

def update_hearts():
    hearts_label.config(text="❤️ " * leben)


# --Timer variablen und Funktion--
def stop_timer():
    global timer_running, timer_job
    # -Stoppt den Timer und bricht die nächste geplante Aktualisierung ab.-
    timer_running = False
    if timer_job:
        root.after_cancel(timer_job)
        timer_job = None
        
def update_timer():
    global timer_job, timer_start_time, timer_running
    
    if not timer_running:
        return
    
    elapsed_time = time.time() - timer_start_time
    
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    # -Millisekunden: Differenz zur vollen Sekunde, multipliziert mit 1000-
    milliseconds = int((elapsed_time - int(elapsed_time)) * 1000)
    
    # -Formatierung: MM:SS:mmm-
    timer_display = f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"
    timer_label.config(text=timer_display)
    
    timer_job = root.after(50, update_timer) # Aktualisiere in 50 Millisekunden (20 Mal pro Sekunde)

# -Globale Timer-Variablen-
timer_running = False
timer_start_time = 0.0
timer_job = None # Für die root.after-Funktion
timer_label = tk.Label(screen_game, text="00:00:000", font=("Arial", font_size3), bg=game_colour) # Label für die Timer-Anzeige  


# -Setzt die Hintergrundfarbe aller Tasten auf Weiß zurück-
def reset_keyboard():
    global keys
    for key in keys.values():
        key.config(bg="white")

# --Tastatur--
keyboard_frame = tk.Frame(screen_game, bg="#AAC1D2")
keyboard_frame.pack(side="bottom", pady=50)

keys = {}
letters = list("QWERTZUIOPÜASDFGHJKLÖÄYXCVBNM")
layout = ["QWERTZUIOPÜ", "ASDFGHJKLÖÄ", "YXCVBNM"]

# -Erstellt die Reihen der Tastatur-
for row in layout:
    row_frame = tk.Frame(keyboard_frame, bg="#AAC1D2")
    row_frame.pack()
    game_row_frames.append(row_frame)
    for char in row:
        lbl = tk.Label(row_frame, text=char, font=("Arial", font_size2), width=4, height=2,
                       bg="white", relief="raised", borderwidth=2)
        lbl.pack(side="left", padx=3, pady=3)
        keys[char] = lbl

# -- Buchstaben überprüfen --
def check_letter(key):
    global leben
    if not geheime_wort or leben <= 0:
        return
    if key in erratene_buchstaben:
        return
    erratene_buchstaben.add(key)

    # -Richtiger oder falscher Buchstabe-
    if key in geheime_wort:
        keys[key].config(bg="#9fff9f")
        play_sound_async(SOUND_CORRECT)
    else:
        keys[key].config(bg="#ff9f9f")
        play_sound_async(SOUND_WRONG)
        leben -= 1
        draw_hangman_stage()
        update_hearts()
    update_word_display()

    # -gewonnen oder verloren-
    if leben == 0:
        stop_timer()
        word_label.config(text=f"Verloren! Das Wort war {geheime_wort}")
        play_sound_async(SOUND_LOSE)
        threading.Timer(0.75, show_retry_button).start() # Warte 0.75 Sekunden und zeige dann den Retry Button an
    elif all(c in erratene_buchstaben for c in geheime_wort):
        stop_timer()
        word_label.config(text="🎉 Gewonnen! Das Wort war " + geheime_wort)
        play_sound_async(SOUND_WIN)
        elapsed_time = time.time() - timer_start_time
        global last_time_ms
        last_time_ms = int(elapsed_time * 1000) # Speichern der Zeit in Millisekunden
        threading.Timer(0.5, show_endgame_buttons).start()
# --Speicherung des Highscores--

# --Fügt den neuen Score zur globalen Liste hinzu und speichert sie.--
def save_score(name, time_ms, category):
    global highscores
    
    # -Sicherstellen, dass die Kategorie existiert-
    if category not in highscores:
        highscores[category] = []
        
    highscores[category].append({
        "name": name,
        "time_ms": time_ms
    })
    
    highscores[category].sort(key=lambda x: x["time_ms"])
    highscores[category] = highscores[category][:50] # Beschränkung der Nummer an Highscores pro Kategorie
    
    save_highscores(highscores) 
    update_highscores_display() 

def show_name_input_popup():
    #-Öffnet ein TopLevel-Fenster zur Eingabe des Namens.-
    hide_endgame_buttons() # Buttons im Hintergrund ausblenden
    
    popup = tk.Toplevel(root)
    popup.title("Highscore speichern")
    # -Positioniere das Fenster mittig (einfache Methode)-
    window_width = 300
    window_height = 150
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    popup.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    popup.resizable(False, False)
    popup.grab_set() # Blockiert Interaktion mit dem Hauptfenster
    
    tk.Label(popup, text="Name eingeben:", font=("Arial", 16)).pack(pady=10)
    
    name_entry = tk.Entry(popup, font=("Arial", 14), width=20)
    name_entry.pack(pady=5, padx=20)
    name_entry.focus_set()

    def submit_score(event=None):
        name = name_entry.get()
        if name:
            current_category = kategorien[kategorie_index]
            # -Speicheren des Scores und schließen des Fensters-
            save_score(name, last_time_ms, current_category)
            popup.destroy()
            
            screen_highscores.tkraise() # Gehe zum Highscore Screen
        else:
            name_entry.insert(0, "BITTE NAMEN EINGEBEN!")
            
    name_entry.bind("<Return>", submit_score)
    
    tk.Button(popup, text="Speichern", command=submit_score).pack(pady=10)
     

# --(Retry + Save)--
def show_retry_button():
    #-Platziert nur den Retry Button (z.B. nach dem Verlieren).-
    btn_retry.place(relx=0.5, rely=0.53, anchor='center')
def show_endgame_buttons():
    #-Platziert Retry und Save Button über der Tastatur.-
    btn_retry.place(relx=0.45, rely=0.53, anchor='center')
    btn_save_score.place(relx=0.55, rely=0.53, anchor='center')

def hide_endgame_buttons():
    #-Blendet die Buttons aus.-
    btn_retry.place_forget()
    btn_save_score.place_forget()


# -Themen mit Wörtern-
themen_woerter = {
    "Länder": ["AFGHANISTAN", "ÄGYPTEN", "ALBANIEN", "ALGERIEN", "ARGENTINIEN", "ARMENIEN", "AUSTRALIEN", "ÖSTERREICH", "BANGLADESCH", "BELGIEN", "BOLIVIEN", "BRASILIEN", "BULGARIEN", "KANADA", "CHILE", "CHINA", "KOLUMBIEN", "KROATIEN", "TSCHECHISCHE REPUBLIK", "DÄNEMARK", "DOMINIKANISCHE REPUBLIK", "ECUADOR", "ÄTHIOPIEN", "FINNLAND", "FRANKREICH", "GEORGIEN", "DEUTSCHLAND", "GHANA", "GRIECHENLAND", "GUATEMALA", "HAITI", "HONDURAS", "UNGARN", "ISLAND", "INDIEN", "INDONESIEN", "IRAN", "IRAK", "IRLAND", "ISRAEL", "ITALIEN", "JAPAN", "JORDANIEN", "KENIA", "NORDKOREA", "SÜDKOREA", "KUWAIT", "LETTLAND", "LIBANON", "LITAUEN", "LUXEMBURG", "MADAGASKAR", "MALAYSIA", "MALI", "MALTA", "MAURITIUS", "MEXIKO", "MOLDAVIEN", "MONGOLEI", "MONTENEGRO", "MAROKKO", "MOSAMBIK", "MYANMAR", "NAMIBIA", "NEPAL", "NIEDERLANDE", "NEUSEELAND", "NICARAGUA", "NIGERIA", "NORWEGEN", "PAKISTAN", "PANAMA", "PARAGUAY", "PERU", "PHILIPPINEN", "POLEN", "PORTUGAL", "KATAR", "RUMÄNIEN", "RUSSLAND", "SAUDI ARABIEN", "SENEGAL", "SERBIEN", "SINGAPUR", "SLOWAKEI", "SLOWENIEN", "SÜDAFRIKA", "SPANIEN", "SRI LANKA", "SCHWEDEN", "SCHWEIZ", "SYRIEN", "TAIWAN", "THAILAND", "TUNESIEN", "TÜRKEI", "UKRAINE", "VEREINIGTE ARABISCHE EMIRATE", "VEREINIGTES KÖNIGREICH", "USA", "URUGUAY", "VENEZUELA", "VIETNAM", "ZAMBIA", "ZIMBABWE"],
    "Städte": ["AMSTERDAM", "BARCELONA", "BEIJING", "BERLIN", "BANGKOK", "BUDAPEST", "BUENOSAIRES", "CAPE TOWN", "CHICAGO", "COPENHAGEN", "DUBLIN", "DUBAI", "EDINBURGH", "FRANKFURT", "GENEVA", "HAMBURG", "HELSINKI", "HONGKONG", "ISTANBUL", "JAKARTA", "KUALALUMPUR", "KYOTO", "LISBON", "LONDON", "LOSANGELES", "MADRID", "MANILA", "MELBOURNE", "MEXICOCITY", "MIAMI", "MILAN", "MOSCOW", "MUNICH", "NAIROBI", "NEWDELHI", "NEWYORK", "OSLO", "PARIS", "PRAGUE", "RIODEJANEIRO", "ROME", "SANFRANCISCO", "SANTIAGO", "SÃO PAULO", "SEOUL", "SHANGHAI", "SINGAPORE", "STOCKHOLM", "SYDNEY", "TAIPEI", "TOKYO", "TORONTO", "VALENCIA", "VANCOUVER", "VENICE", "VIENNA", "WARSAW", "WASHINGTON", "ZURICH", "BERN"],
    "Tiere": ["HUND", "KATZE", "PFERD", "KUH", "SCHWEIN", "SCHAF", "ZIEGE", "HASE", "KANINCHEN", "HAMSTER", "MAUS", "RATTE", "MEERSCHWEINCHEN", "FUCHS", "WOLF", "BÄR", "LÖWE", "TIGER", "LEOPARD", "GEPARD", "ELEFANT", "NASHORN", "FLUSSPFERD", "AFFE", "GORILLA", "SCHIMPANSE", "ORANGUTAN", "GIRAFFE", "ZEBRA", "KROKODIL", "ALLIGATOR", "SCHILDKRÖTE", "ECHSE", "SCHLANGE", "PYTHON", "KOBRA", "IGEL", "MAULWURF", "REH", "HIRSCH", "ELCH", "WILDSCHWEIN", "DACH", "MARDER", "WIESEL", "OTTER", "SEEHUND", "WALROSS", "DELFIN", "WAL", "HAI", "ROCHEN", "FISCH", "FORELLE", "LACHS", "KARPEN", "HECHT", "STÖR", "SPATZ", "AMSEL", "MEISE", "TAUBE", "ENTE", "GANS", "SCHWAN", "ADLER", "FALKE", "GEIER", "EULE", "PAPAGEI", "WELLENSITTICH", "KANARIE", "HÜHNER", "HAHN", "HENNE", "TRUTHAN", "STRAUSS", "PFAU", "KÄFER", "AMEISE", "BIENE", "WESPE", "FLIEGE", "MÜCKE", "LIBELLE", "SCHMETTERLING", "SPINNE", "SKORPION", "KREBS", "HUMMER", "QUALLE", "SEESTERN", "SEEPFERDCHEN", "OCTOPUS", "TINTENFISCH", "MUSCHEL", "SCHNECKE", "ALPAKA", "LAMA", "YAK", "REGENWURM"],
    "Informatik": ["ALGORITHMUS", "ANWENDUNG", "ARRAY", "ARBEITSSPEICHER", "BACKEND", "BROWSER", "CACHE", "CLOUD", "CODE", "COMPUTER", "CPU", "DATEN", "DATENBANK", "DEBUGGING", "DEKODIERUNG", "DESIGN", "DIGITAL", "DOMAIN", "DOWNLOAD", "EINGABE", "ENCRYPTION", "ETHERNET", "FESTPLATTE", "FIREWALL", "FIRMWARE", "FORMAT", "FRAMEWORK", "FUNKTION", "GATEWAY", "GRAFIKKARTE", "HARDWARE", "HEADSET", "HOSTING", "INDEX", "INFRASTRUKTUR", "INPUT", "INSTALLATION", "INTERNET", "IPADRESSE", "JAVA", "JAVASCRIPT", "KABEL", "KAMERA", "KOMPILER", "KONFIGURATION", "KONTROLLE", "LAPTOP", "LAUTSPRECHER", "LINUX", "LOGIN", "LOGIK", "MAINBOARD", "MALWARE", "MAUS", "MEMORY", "MICROFON", "MODEM", "MONITOR", "NETZWERK", "OBJEKT", "OPENSOURCE", "OPTIMIERUNG", "OUTPUT", "PASSWORT", "PIXEL", "PLATTFORM", "PROZESSOR", "PROGRAMM", "PROGRAMMIERUNG", "RECHNER", "ROUTER", "SCRIPT", "SERVER", "SOFTWARE", "SPEICHERSTICK", "SYNTAX", "SYSTEM"],
    "Games": ["MINECRAFT", "FORTNITE", "ROBLOX", "AMONGUS", "CALLDUTY", "BATTLEFIELD", "HALO", "OVERWATCH", "VALORANT", "LEAGUELEGENDS", "WORLDOFWARCRAFT", "COUNTERSTRIKE", "APEXLEGENDS", "PUBG", "GTA", "REDDEADREDEMPTION", "ASSASSINSCREED", "FARCRY", "SKYRIM", "FALLOUT", "THEWITCHER", "CYBERPUNK", "ELDENRING", "DARKSOULS", "SEKIRO", "HORIZON", "GODOFWAR", "UNCHARTED", "LASTOFUS", "SPIDERMAN", "BATMANARKHAM", "RESIDENTEVIL", "DEADRISING", "DEATHSTRANDING", "PORTAL", "HALFLIFE", "TERRARIA", "STARDEWVALLEY", "ANIMALCROSSING", "POKEMON", "ZELDA", "MARIOKART", "SUPERMARIO", "SMASHBROS", "METROID", "DONKEYKONG", "FIFA", "NBAK", "ROCKETLEAGUE", "SIMS", "CIVILIZATION", "TEKKEN", "STREETFIGHTER", "MORTALKOMBAT", "RAINBOWSIX", "PAYDAY", "LEFT4DEAD", "DOTA", "TEAMFORTRESS", "PALWORLD", "HOGWARTSLEGACY", "BALDURSGATE", "FORZA", "GRAN TURISMO", "TOMBRAIDER", "CONTROL", "ALANWAKE", "DEADISLAND", "SUBNAUTICA", "OUTLAST", "LITTLEBIGPLANET"],
    "Filme": ["TITANIC", "AVATAR", "INCEPTION", "THE GODFATHER", "THE DARK KNIGHT", "FORREST GUMP", "PULP FICTION", "JURASSIC PARK", "STAR WARS", "THE EMPIRE STRIKES BACK", "RETURN OF THE JEDI", "HARRY POTTER", "THE LORD OF THE RINGS", "THE FELLOWSHIP OF THE RING", "THE TWO TOWERS", "THE RETURN OF THE KING", "THE MATRIX", "GLADIATOR", "SAVING PRIVATE RYAN", "SCHINDLERS LIST", "BRAVEHEART", "INTERSTELLAR", "FIGHT CLUB", "THE SHAWSHANK REDEMPTION", "THE GREEN MILE", "THE LION KING", "FROZEN", "TOY STORY", "FINDING NEMO", "UP", "INSIDE OUT", "COCO", "WALL E", "RATATOUILLE", "MONSTERS INC", "CARS", "THE INCREDIBLES", "BEAUTY AND THE BEAST", "ALADDIN", "MULAN", "MOANA", "ENCANTO", "THE LITTLE MERMAID", "SNOW WHITE", "CINDERELLA", "SLEEPING BEAUTY", "MALEFICENT", "PIRATES OF THE CARIBBEAN", "DEADPOOL", "IRON MAN", "CAPTAIN AMERICA", "AVENGERS ENDGAME", "AVENGERS INFINITY WAR", "BLACK PANTHER", "DOCTOR STRANGE", "SPIDER MAN", "BATMAN BEGINS", "THE DARK KNIGHT RISES", "JOKER", "WONDER WOMAN", "AQUAMAN", "THE HUNGER GAMES", "TWILIGHT", "DIVERGENT", "THE MAZE RUNNER", "FANTASTIC BEASTS", "THE CHRONICLES OF NARNIA", "THE HOBBIT", "KING KONG", "GODZILLA", "THE REVENANT", "LA LA LAND", "BOHEMIAN RHAPSODY", "A STAR IS BORN", "THE GREATEST SHOWMAN", "THE WOLF OF WALL STREET", "CATCH ME IF YOU CAN", "CAST AWAY", "THE TERMINAL"],
    "Dinosaurier": ["TYRANNOSAURUS", "TRICERATOPS", "VELOCIRAPTOR", "BRACHIOSAURUS", "STEGOSAURUS", "DIPLODOCUS", "APATOSAURUS", "ALLOSAURUS", "IGUANODON", "SPINOSAURUS", "CARNOTAURUS", "ANKYLOSAURUS", "PACHYCEPHALOSAURUS", "PARASAUROLOPHUS", "MAIASAURA", "GALLIMIMUS", "THERIZINOSAURUS", "MICRORAPTOR", "ARCHAEOPTERYX", "DEINONYCHUS", "CERATOSAURUS", "COELOPHYSIS", "COMPSOGNATHUS", "DASPLETOSAURUS", "EDMONTOSAURUS", "GIGANOTOSAURUS", "LAMBEOSAURUS", "LEALLYNASAURA", "MEGALOSAURUS", "MONONYKUS", "NOTHRONYCUS", "ORNITHOLESTES", "ORNITHOMIMUS", "OURANOSAURUS", "PLATEOSAURUS", "PROCOMPSOGNATHUS", "PSITTACOSAURUS", "SAICHANIA", "SCELIDOSAURUS", "SHANTUNGOSAURUS", "SINORNITHOSAURUS", "STYRACOSAURUS", "STRUTHIOMIMUS", "SUCHOMIMUS", "TOROSAURUS", "UTAHRAPTOR", "XUANHANSAURUS", "YANGCHUANOSAURUS", "ZUNICERATOPS", "TROODON", "TENONTOSAURUS", "THEROPODA", "ORNITHISCHIA", "SAUROPODA", "NEOVENATOR", "RAPTOROSAURUS", "DRACOREX", "EORAPTOR", "FUKUIRAPTOR", "HERRERASAURUS", "HYPSILOPHODON", "ISANOSAURUS", "JAXARTOSAURUS", "KENTROSAURUS", "LILIENTERNUS", "MASSOSPONDYLUS", "NANOTYRANNUS", "OVIRAPTOR", "PANTHEROSAURUS", "QUAESITOSAURUS", "RHOETOSAURUS", "SALTASAURUS"],
    "Berufe": ["KAUFMANN", "POLIZIST", "ÄRZTIN", "LEHRER", "ELEKTRIKER", "INFORMATIKER", "MECHANIKER", "BAUARBEITER", "MAURER", "ZIMMERMANN", "MALER", "COIFFEUR", "KOCH", "SERVICEFACHPERSON", "BÄCKER", "METZGERS", "FLORIST", "LANDWIRT", "LOGISTIKER", "SPEDITIONSKAUFMANN", "VERSICHERUNGSBERATER", "BANKKAUFMANN", "IMMOBILIENMAKLER", "RECHTSANWALT", "NOTAR", "ARCHITEKT", "INGENIEUR", "TECHNIKER", "PHARMAASSISTENT", "APOTHEKER", "ZAHNARZT", "DENTALASSISTENT", "OPTIKER", "AUGENARZT", "SOZIALARBEITER", "PSYCHOLOGE", "THERAPEUT", "KINDERBETREUER", "FACHFRAU GESUNDHEIT", "FACHMANN BETREUUNG", "FACHMANN FINANZEN", "BUCHHALTER", "STEUERBERATER", "HR FACHPERSON", "MARKETINGFACHPERSON", "MEDIENGESTALTER", "GRAFIKER", "JOURNALIST", "FOTOGRAF", "FILMEMACHER", "MUSIKER", "SCHAUSPIELER", "TANZLEHRER", "SPORTLEHRER", "FITNESSTRAINER", "REISEFACHPERSON", "FLUGBEGLEITER", "PILOT", "LOKOMOTIVFÜHRER", "BUSFAHRER", "CHAUFFEUR", "TIERPFLEGER", "VETERINÄR", "BIOLOGE", "CHEMIELABORANT", "PHYSIKER", "MATHEMATIKER", "STATISTIKER", "DATENANALYST", "CYBERSICHERHEITSEXPERTE", "WEBENTWICKLER", "SYSTEMTECHNIKER", "NETZWERKSPEZIALIST", "PROJEKTMANAGER", "PRODUKTIONSPLANER", "QUALITÄTSPRÜFER", "LAGERMITARBEITER", "VERKÄUFER", "KUNDENBERATER", "REINIGUNGSKRAFT", "HAUSWART"],
    "Berühmtheit": ["ALBERT EINSTEIN", "MARIE CURIE", "ISAAC NEWTON", "LEONARDO DA VINCI", "GALILEO GALILEI", "STEPHEN HAWKING", "NAPOLEON BONAPARTE", "ALEXANDER DER GROSSE", "JOHANNES GUTENBERG", "MARTIN LUTHER", "KARL MARX", "SIGMUND FREUD", "FRIEDRICH NIETZSCHE", "IMMANUEL KANT", "SOCRATES", "PLATON", "ARISTOTELES", "MOZART", "LUDWIG VAN BEETHOVEN", "JOHANN SEBASTIAN BACH", "FRANZ SCHUBERT", "RICHARD WAGNER", "PABLO PICASSO", "VINCENT VAN GOGH", "CLAUDE MONET", "FRIDA KAHLO", "MICHELANGELO", "REMBRANDT", "WILLIAM SHAKESPEARE", "GOETHE", "FRIEDRICH SCHILLER", "THOMAS MANN", "HERMANN HESSE", "BERTOLT BRECHT", "HEINRICH HEINE", "ANGELA MERKEL", "BARACK OBAMA", "WINSTON CHURCHILL", "JOHN F KENNEDY", "NELSON MANDELA", "MAHATMA GANDHI", "CRISTIANO RONALDO", "LIONEL MESSI", "PELE", "DIEGO MARADONA", "ROGER FEDERER", "MICHAEL SCHUMACHER", "SEBASTIAN VETTEL", "DIRK NOWITZKI", "BORIS BECKER", "STEFAN RAAB", "THOMAS GOTTSCHALK", "HELMUT KOHL", "JOSEF STALIN", "ADOLF HITLER", "VLADIMIR LENIN", "THEODOR FONTANE", "MAX PLANCK", "ERNST RUSKA", "WERNER HEISENBERG", "OTTO HAHN", "ALEXANDER FLEMING", "LOUIS PASTEUR", "CHARLES DARWIN", "NIKOLA TESLA", "THOMAS EDISON", "MARILYN MONROE", "ELVIS PRESLEY", "MICHAEL JACKSON", "FREDDIE MERCURY", "TAYLOR SWIFT", "RIHANNA", "BEYONCE", "BRAD PITT", "ANGELINA JOLIE", "TOM CRUISE", "LEONARDO DICAPRIO", "KEANU REEVES", "EMMA WATSON", "DANIEL RADCLIFFE"],
    "Musik": ["BOHEMIAN RHAPSODY", "IMAGINE", "HEY JUDE", "PURPLE RAIN", "THRILLER", "BILLIE JEAN", "BAD GUY", "SHAPE OF YOU", "LOVE STORY", "BLINDING LIGHTS", "SWEET CHILD", "DANCING QUEEN", "LET IT BE", "YESTERDAY", "STAYIN ALIVE", "TAKE ON ME", "AFRICA", "EVERY BREATH YOU TAKE", "WITH OR WITHOUT YOU", "NOTHING ELSE MATTERS", "LIVIN ON A PRAYER", "BORN TO RUN", "SUPERSTITION", "RESPECT", "HALLELUJAH", "HELLO", "SKYFALL", "FIX YOU", "VIVA LA VIDA", "CLOCKS", "HUMAN NATURE", "BEAT IT", "BLACK MAGIC", "NO CONTROL", "STORY OF MY LIFE", "LITTLE THINGS", "DRAG ME DOWN", "NIGHT CHANGES", "STEAL MY GIRL", "KISS YOU", "BEST SONG EVER", "ONE THING", "LIVE WHILE YOUNG", "MORE THAN THIS", "SHE LOOKS PERFECT", "WHAT MAKES YOU", "IF I FALL", "BACK TO BLACK", "ONLY GIRL", "PLEASE ME", "TALKING TO THE MOON", "STAY", "LOVE ME LIKE", "NO TEARS LEFT", "BREAK FREE", "SIDE TO SIDE", "THANK YOU NEXT", "COLD HEART", "NEW RULES", "DONT START NOW", "WATERMELON SUGAR", "AS IT WAS", "FLOWERS", "MIDNIGHT SKY", "WRECKING BALL", "PARTY IN USA", "WE CANT STOP", "SOMEBODY TO LOVE", "I WANNA DANCE", "CALL ME MAYBE", "LIKE A PRAYER", "MATERIAL GIRL", "TOXIC", "BABY ONE MORE", "UMBRELLA", "WE FOUND LOVE", "SHAKE IT OFF", "ALL OF ME", "LET HER GO", "POMPEII", "ELASTIC HEART", "CHEAP THRILLS", "RUNAWAY", "FADED", "ALONE", "ON MY WAY", "PERFECT", "BAD HABITS", "PHOTOGRAPH", "SHIVERS", "TALKING BODY", "STAY CLOSE", "LOVE ME HARDER", "NO TIME TO", "SET FIRE TO", "ROLLING IN DEEP", "SOMEONE LIKE YOU", "THINKING OUT LOUD", "JUST THE WAY"],
    "Superhelden": ["SUPERMAN", "BATMAN", "SPIDERMAN", "IRON MAN", "CAPTAIN AMERICA", "WONDER WOMAN", "BLACK PANTHER", "THOR", "HULK", "FLASH", "AQUAMAN", "GREEN LANTERN", "CYBORG", "BLACK WIDOW", "HAWKEYE", "DOCTOR STRANGE", "SCARLET WITCH", "VISION", "ANT MAN", "WASP", "STAR LORD", "GAMORA", "DRAX", "ROCKET RACCOON", "GROOT", "SILVER SURFER", "WOLVERINE", "STORM", "MAGNETO", "PROFESSOR X", "JEAN GREY", "CYCLOPS", "BEAST", "NIGHTCRAWLER", "ROGUE", "DEADPOOL", "GHOST RIDER", "MOON KNIGHT", "SHANG CHI", "MS MARVEL", "CAPTAIN MARVEL", "GREEN ARROW", "SUPERGIRL", "BATGIRL", "BLUE BEETLE", "STATIC SHOCK", "MARTIAN MANHUNTER", "RAVEN", "STARFIRE", "BEAST BOY"],
    "Automarke": ["VOLKSWAGEN", "MERCEDES", "BEIRISCHE MOTOREN WERKE", "AUDI", "PORSCHE", "OPEL", "FORD", "TOYOTA", "HONDA", "NISSAN", "MAZDA", "SUZUKI", "HYUNDAI", "KIA", "RENAULT", "PEUGEOT", "CITROEN", "FIAT", "SEAT", "SKODA", "TESLA", "CHEVROLET", "JEEP", "CHRYSLER", "DODGE", "SUBARU", "VOLVO", "LAND ROVER", "JAGUAR", "MITSUBISHI"],
}
kategorie_index = 0
auswahl_aktiv = True
geheime_wort = ""
erratene_buchstaben = set()
leben = 6
hangman_parts = []

# -Globale Timer-Variablen-
timer_running = False
timer_start_time = 0.0
timer_job = None 
last_time_ms = 0

# -Retry Button-
btn_retry = tk.Button(screen_game, text="🔄", font=("Arial", font_size5),
                     command=show_selection,
                     bg=game_colour, fg="#333333", 
                     relief="raised", bd=3)
# -Save Highscore Button-
btn_save_score = tk.Button(screen_game, text="💾", font=("Arial", font_size5),
                           command=show_name_input_popup,
                           bg=game_colour, fg="#333333",
                           relief="raised", bd=3)
# --Frame für Auswahl--
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

# --Funktionen für Themenauswahl--
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

# ---Spiel starten---

# -Retry button2-
def handle_enter(event):
    global auswahl_aktiv
    if btn_retry.winfo_ismapped():
        show_selection()
        return

    if auswahl_aktiv:
        start_game()

# --Spiel Start--
def start_game(event=None):
    global geheime_wort, erratene_buchstaben, leben, auswahl_aktiv, timer_start_time, timer_running
    
    auswahl_aktiv = False
    auswahl_frame.place_forget()
    
    # -Timer starten und anzeigen-
    timer_start_time = time.time()
    timer_running = True
    update_timer()
    timer_label.place(relx=1.0, rely=0.0, x=-20, y=20, anchor='ne') # Zeigt den Timer unter dem back-Button an
    
    geheime_wort = random.choice(themen_woerter[kategorien[kategorie_index]])
    erratene_buchstaben = set()
    erratene_buchstaben.update(" ")
    leben = 6

    update_word_display()
    draw_gallows()
    hearts_label.pack()
    update_hearts()


# --Tastatursteuerung--
umlaut_map = {"adiaeresis": "Ä", "odiaeresis": "Ö", "udiaeresis": "Ü"}

def on_key_press(event):
    if auswahl_aktiv:  # deaktiviert, wenn kein Thema gewählt
        return
    key = event.keysym.upper()
    if key.lower() in umlaut_map:
        key = umlaut_map[key.lower()]
    if key in keys:
        check_letter(key)

root.bind("<KeyPress>", on_key_press)

# -Maus und Tastatur Navigation für Menü-
btn_links.bind("<Button-1>", prev_kategorie)
btn_rechts.bind("<Button-1>", next_kategorie)
auswahl_label.bind("<Button-1>", start_game)
root.bind("<Left>", prev_kategorie)
root.bind("<Right>", next_kategorie)
root.bind("<Return>", handle_enter)


# ---SETTINGS-Screen---
settings_label = tk.Label(screen_settings, text="Einstellungen", font=("Arial", font_size3), bg=screen_colour)
settings_label.pack(pady=50)
settings_back_button = tk.Button(screen_settings, text="← BACK", font=("Arial", font_size1), command=go_back)
settings_back_button.place(x=20, y=20)

# --Size Controll--
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


    # -Settings - Settings Screen-
    settings_label.config(font=("Arial", font_size3))
    settings_back_button.config(font=("Arial", font_size1))
    size_button.config(text=current_font_size, font=("Arial", font_size3))
    size_button_identifier.config(font=("Arial", font_size2))
    
    # -Settings - Highscore Screen-
    highscore_label.config(font=("Arial", font_size3))
    highscore_back_button.config(font=("Arial", font_size1))
    highscore_kategorie_label.config(font=("Arial", font_size2))
    update_highscores_display()

    # -Settings - Game Screen-
    game_back_button.config(font=("Arial", font_size1))
    word_label.config(font=("Courier", font_size4))
    hearts_label.config(font=("Arial", font_size2))
    timer_label.config(font=("Arial", font_size3))
    
    # -Settings - Menu Screen-
    btn_spielen.config(font=("Arial", font_size2))
    btn_einstellungen.config(font=("Arial", font_size2))
    btn_highscores.config(font=("Arial", font_size2))
    btn_beenden.config(font=("Arial", font_size2))

    # -Settings - Game Screen Auswahl Frame-
    btn_links.config(font=("Arial", font_size5))
    auswahl_label.config(font=("Arial", font_size3, "bold"))
    btn_rechts.config(font=("Arial", font_size5))
    
    # -Settings - Game Screen Keyboard (als Schleife)-
    for key_label in keys.values():
        key_label.config(font=("Arial", font_size2))

# -Onscreen Size Buttons-
size_control_frame = tk.Frame(screen_settings, bg=screen_colour) 
size_control_frame.pack(pady=20) 
size_button_identifier = tk.Label(size_control_frame, text="Text size", font=("Arial", font_size2), bg=screen_colour)
size_button_identifier.pack(side="left", padx=10)
size_button = tk.Button(size_control_frame, text=current_font_size, font=("Arial", font_size3), command=change_text_size)
size_button.pack(side="left", padx=10)
root.bind("<BackSpace>", lambda event: go_back())

# --Backgrounds--
def all_redos():
    global screen_colour, menu_colour, game_colour, standard_background_clours, canvas
    # -Other Screens-
    screen_settings.config(bg=screen_colour)
    settings_label.config(bg=screen_colour)
    size_button_identifier.config(bg=screen_colour)
    size_control_frame.config(bg=screen_colour)
    background_control_frame1.config(bg=screen_colour)
    background_control_frame2.config(bg=screen_colour)
    background_control_frame3.config(bg=screen_colour)
    background_titel1.config(bg=screen_colour)
    background_titel2.config(bg=screen_colour)
    background_titel3.config(bg=screen_colour)
    screen_highscores.config(bg=screen_colour)
    highscore_label.config(bg=screen_colour)
    highscore_control_frame.config(bg=screen_colour)
    highscore_kategorie_label.config(bg=screen_colour)
    highscore_list_frame.config(bg=screen_colour)
    canvas_hs.config(bg=screen_colour)
    # -Menu Screen-
    screen_menu.config(bg=menu_colour)
    menu_canvas.config(bg=menu_colour)
    # -Game Screen-
    screen_game.config(bg=game_colour)
    word_label.config(bg=game_colour)
    hearts_label.config(bg=game_colour)
    timer_label.config(bg=game_colour)
    auswahl_frame.config(bg=game_colour)
    btn_retry.config(bg=game_colour)
    auswahl_frame.config(bg=game_colour)
    btn_links.config(bg=game_colour)
    btn_rechts.config(bg=game_colour)
    canvas.config(bg=game_colour)
    btn_save_score.config(bg=game_colour)
    keyboard_frame.config(bg=game_colour)  
    for frame in game_row_frames: 
        frame.config(bg=game_colour) 
    
# --Background Colour Change Functions--
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

# --Onscreen Background Buttons--
# -Other Screens Background Colour-
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

# -Game Background Colour-
background_titel2 = tk.Label(screen_settings, text="Background Colour for the Game", font=("Arial", font_size2), bg=screen_colour)
background_titel2.pack(pady=00)
background_control_frame2 = tk.Frame(screen_settings, bg=screen_colour) 
background_control_frame2.pack(pady=30) 
background_change_standard = tk.Button(background_control_frame2, text="Background", font=("Arial", font_size3), bg=standard_background_clours[1], fg=standard_background_clours[1], relief="solid", borderwidth=1.5, command=background_game_change1)
background_change_standard.pack(side="left", padx=10)
background_change_standard = tk.Button(background_control_frame2, text="Background", font=("Arial", font_size3), bg=secondary_background_colours[1], fg=secondary_background_colours[1], relief="solid", borderwidth=1.5, command=background_game_change2)
background_change_standard.pack(side="left", padx=10)
background_change_standard = tk.Button(background_control_frame2, text="Background", font=("Arial", font_size3), bg=tertiarty_backgroud_colours[1], fg=tertiarty_backgroud_colours[1], relief="solid", borderwidth=1.5, command=background_game_change3)
background_change_standard.pack(side="left", padx=10)

# -Menu Background Colour-
background_titel3 = tk.Label(screen_settings, text="Background Colour for the Menu", font=("Arial", font_size2), bg=screen_colour)
background_titel3.pack(pady=00)
background_control_frame3 = tk.Frame(screen_settings, bg=screen_colour) 
background_control_frame3.pack(pady=30) 
background_change_standard = tk.Button(background_control_frame3, text="Background", font=("Arial", font_size3), bg=standard_background_clours[0], fg=standard_background_clours[0], relief="solid", borderwidth=1.5, command=background_menu_change1)
background_change_standard.pack(side="left", padx=10)
background_change_standard = tk.Button(background_control_frame3, text="Background", font=("Arial", font_size3), bg=secondary_background_colours[2], fg=secondary_background_colours[2], relief="solid", borderwidth=1.5, command=background_menu_change2)
background_change_standard.pack(side="left", padx=10)
background_change_standard = tk.Button(background_control_frame3, text="Background", font=("Arial", font_size3), bg=tertiarty_backgroud_colours[2], fg=tertiarty_backgroud_colours[2], relief="solid", borderwidth=1.5, command=background_menu_change3)
background_change_standard.pack(side="left", padx=10)

 
# --Highscore-Screen--

HIGHSCORE_FILE = "highscores.json"

def load_highscores():
    global themen_woerter
    #-Lädt Highscores aus der JSON-Datei.-
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # -Falls die Datei leer oder korrupt ist-
                return {k: [] for k in themen_woerter.keys()}
    return {k: [] for k in themen_woerter.keys()}

#-Speichert Highscores in der JSON-Datei.-
def save_highscores(scores):
    with open(HIGHSCORE_FILE, 'w') as f:
        json.dump(scores, f, indent=4)

# -Globale Variable für Highscores initialisieren-
highscores = load_highscores()


# -Container für die Steuerelemente (Kategorieauswahl)-
highscore_control_frame = tk.Frame(screen_highscores, bg=screen_colour)
highscore_control_frame.pack(pady=20)

highscore_label = tk.Label(highscore_control_frame, text="Highscores", font=("Arial", font_size3), bg=screen_colour)
highscore_label.pack(side="top", pady=10)

highscore_back_button = tk.Button(screen_highscores, text="← BACK", font=("Arial", font_size1), command=go_back)
highscore_back_button.place(x=20, y=20)

# --Deleating Highscores---

# --Alles löschen-Button--
clear_all_button = tk.Button(
    screen_highscores,
    text="Alle löschen",
    font=("Arial", font_size1),
    bg="#FF5555",
    fg="white",
    command=lambda: clear_all_highscores()
)
clear_all_button.place(x=400, y=20)

def clear_all_highscores():
    # -Löscht alle Highscores in der aktuellen Kategorie nach Bestätigung.-
    current_category = kategorien[kategorie_index]
    if not highscores.get(current_category):
        messagebox.showinfo("Info", f"Keine Einträge in {current_category} zum Löschen.")
        return

    if messagebox.askyesno("Bestätigen", f"Alle Highscores für {current_category} löschen?"):
        highscores[current_category] = []
        save_highscores(highscores)
        update_highscores_display()


# -Rahmen für die eigentliche Highscore-Liste-
highscore_list_frame = tk.Frame(screen_highscores, bg=screen_colour)
highscore_list_frame.pack(pady=10, fill="both", expand=True)

# --Einzelne Highscore löschen Funktion--
def delete_single_highscore(category, index):
    # -Löscht einen einzelnen Highscore aus der gegebenen Kategorie und aktualisiert Anzeige + Datei.-
    global highscores
    if category not in highscores:
        return
    if 0 <= index < len(highscores[category]):
        del highscores[category][index]
        save_highscores(highscores)
        update_highscores_display()

def update_highscores_display():
    # -Highscore-Liste mit Abstand zwischen den Zeilen und 🗑️ rechts.-
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    current_category = kategorien[kategorie_index]
    highscore_kategorie_label.config(text=f"Kategorie: {current_category}")
    scores = highscores.get(current_category, [])

    # -Header-
    header = tk.Frame(scrollable_frame, bg=screen_colour)
    header.pack(fill="x", padx=40, pady=(0, 5))
    tk.Label(header, text="Platz", font=("Courier", font_size2, "bold"),
             bg=screen_colour, anchor="w", width=6).grid(row=0, column=0, sticky="w")
    tk.Label(header, text="Name", font=("Courier", font_size2, "bold"),
             bg=screen_colour, anchor="w", width=24).grid(row=0, column=1, sticky="w")
    tk.Label(header, text="Zeit (mm:ss:ms)", font=("Courier", font_size2, "bold"),
             bg=screen_colour, anchor="w", width=18).grid(row=0, column=2, sticky="w", padx=(40, 0))
    tk.Label(header, text="", bg=screen_colour, width=3).grid(row=0, column=3)

    for i, score in enumerate(scores):
        # -Abwechselnde Zeilenfarben-
        bg_color = "#ffffff" if i % 2 == 0 else "#f2f0ef"

        # -Äußerer Rahmen in Hintergrundfarbe-
        outer_frame = tk.Frame(scrollable_frame, bg=screen_colour)
        outer_frame.pack(fill="x", padx=40, pady=(2, 3))  

        # -Innerer Frame = eigentliche Zeile-
        row = tk.Frame(outer_frame, bg=bg_color)
        row.pack(fill="x", padx=0, pady=0, ipadx=0, ipady=0)

        # -Zeit berechnen-
        time_ms = score.get("time_ms", 0)
        total_seconds = time_ms / 1000
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int(time_ms % 1000)
        time_str = f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"

        # -Spaltenlayout-
        row.grid_columnconfigure(0, weight=0)
        row.grid_columnconfigure(1, weight=1)
        row.grid_columnconfigure(2, weight=0)
        row.grid_columnconfigure(3, weight=0)

        # -Platz-
        tk.Label(row, text=f"{i+1}.", font=("Courier", font_size1),
                 bg=bg_color, width=5, anchor="w").grid(row=0, column=0, sticky="w", padx=(10, 10), pady=6)

        # -Name-
        tk.Label(row, text=score.get("name", ""), font=("Courier", font_size1),
                 bg=bg_color, anchor="w").grid(row=0, column=1, sticky="we", pady=6)

        # -Zeit-
        tk.Label(row, text=time_str, font=("Courier", font_size1),
                 bg=bg_color, width=18, anchor="e").grid(row=0, column=2, sticky="e", padx=(50, 5), pady=6)

        # -🗑️ Lösch-Button-
        delete_btn = tk.Button(
            row,
            text="🗑️",
            font=("Segoe UI Emoji", font_size1 + 2),
            bg="#ff6666",
            fg="white",
            relief="raised",
            width=2,
            height=1,
            pady=-1,
            command=lambda idx=i, cat=current_category: delete_single_highscore(cat, idx)
        )
        delete_btn.grid(row=0, column=3, sticky="e", padx=(8, 12), pady=4)


    canvas_hs.update_idletasks()

# -- Kategorie-Wechsel im Highscore-Screen --

def next_highscore_category(event=None):
    global kategorie_index
    kategorie_index = (kategorie_index + 1) % len(kategorien)
    update_highscores_display()

def prev_highscore_category(event=None):
    global kategorie_index
    kategorie_index = (kategorie_index - 1) % len(kategorien)
    update_highscores_display()

# --Kategorie-Auswahlzeile im Highscore-Screen ersetzen--
highscore_kategorie_frame = tk.Frame(highscore_control_frame, bg=screen_colour)
highscore_kategorie_frame.pack(pady=5)

btn_highscore_links = tk.Label(highscore_kategorie_frame, text="◀", font=("Arial", font_size4),
                               bg=screen_colour, cursor="hand2")
btn_highscore_links.pack(side="left", padx=15)

highscore_kategorie_label = tk.Label(highscore_kategorie_frame, text="Kategorie: Länder",
                                     font=("Arial", font_size2), bg=screen_colour)
highscore_kategorie_label.pack(side="left", padx=5)

btn_highscore_rechts = tk.Label(highscore_kategorie_frame, text="▶", font=("Arial", font_size4),
                                bg=screen_colour, cursor="hand2")
btn_highscore_rechts.pack(side="left", padx=15)

# -Verknüpfungen-
btn_highscore_links.bind("<Button-1>", prev_highscore_category)
btn_highscore_rechts.bind("<Button-1>", next_highscore_category)
root.bind("<Left>", prev_highscore_category)
root.bind("<Right>", next_highscore_category)

# -Scrollbarer Bereich für die Highscores-
canvas_hs = tk.Canvas(highscore_list_frame, bg=screen_colour, highlightthickness=0)
scrollbar = tk.Scrollbar(highscore_list_frame, orient="vertical", command=canvas_hs.yview)
scrollable_frame = tk.Frame(canvas_hs, bg=screen_colour)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas_hs.configure(
        scrollregion=canvas_hs.bbox("all")
    )
)

canvas_hs.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas_hs.configure(yscrollcommand=scrollbar.set)

# -Platziere Canvas und Scrollbar-
scrollbar.pack(side="right", fill="y")
canvas_hs.pack(side="left", fill="both", expand=True, padx=20)

# --Aktualisierung der Anzeige beim Öffnen des Highscore-Screens--
def show_highscores_screen():
    # -Alte Tastaturbindungen (vom Spiel) entfernen-
    root.unbind("<Left>")
    root.unbind("<Right>")
    
    # -Highscore-Tasten aktivieren-
    root.bind("<Left>", prev_highscore_category)
    root.bind("<Right>", next_highscore_category)
    
    update_highscores_display()
    screen_highscores.tkraise()

# -4. Ersetze den alten Command des Highscore-Buttons-
btn_highscores.config(command=show_highscores_screen)

# ---Sounds---
def play_sound_async(sound):
    threading.Thread(target=play_sound, args=(sound,), daemon=True).start() 

# -Angepasste load_sound-Funktion-
def load_sound(name):
    if name == "success.wav":  # Win-Sound
        return {"freq": [880], "dur": [300]}
    elif name == "failed.wav":  # Fehler-Sound
        return {"freq": [220], "dur": [300]}
    elif name == "win.wav":     # Sieges-Sound
        return {"freq": [660, 880, 1320], "dur": [150, 150, 150]}
    elif name == "lost.wav":    # Game-Over-Sound
        return {"freq": [330, 220], "dur": [300, 300]}
    else:
        return None

# -Sounds laden-
SOUND_CORRECT = load_sound("success.wav")
SOUND_WRONG   = load_sound("failed.wav")
SOUND_WIN     = load_sound("win.wav")
SOUND_LOSE    = load_sound("lost.wav")

# -Abspiel Funktion-
def play_sound(sound):
    if not sound:
        return
    try:
        for f, d in zip(sound["freq"], sound["dur"]):
            winsound.Beep(f, d)
            time.sleep(0.05)  # Kurze Pause zwischen den Tönen
    except Exception as e:
        print("Play sound error:", e)

# -Startup Sound-
if __name__ == "__main__":
    play_sound(SOUND_CORRECT)
    time.sleep(0.4)
    play_sound(SOUND_WRONG)
    time.sleep(0.4)
    play_sound(SOUND_WIN)

#----Start mit Menü----
screen_menu.tkraise()
root.mainloop()
