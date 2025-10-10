# -*- coding: utf-8 -*-
"""
Hangman: Vollversion
Features:
- tkinter GUI: Menü, Spiel, Einstellungen, Highscores
- Kategorien
- Klickbare Tastatur + Wort-Eingabe
- Canvas Hangman Zeichnung
- Sound via pygame.mixer (place WAV files in ./sounds/)
- Highscores als JSON (scores.json)


 - If no sounds, no problem - game works without them
 - But if you want sounds, place WAV files in a "sounds" folder next to this script:
    - success.wav (correct guess)
    - failed.wav (wrong guess)
    - win.wav (game won)
    - lost.wav (game lost)
    - Scores saved in scores.json next to this script
 - And if you have not pip installed pygame, do so via:
   - py -m pip install pygame
"""

import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import random
import os
import json
import pygame




# -----------------------
# Konfiguration / Daten
# -----------------------
APP_TITLE = "Hangman"
SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "sounds")
SCORES_FILE = os.path.join(os.path.dirname(__file__), "scores.json")
pygame.init()



# Kategorien mit Beispielwörtern (erweiterbar)
CATEGORIES = {
    "Alltag": ["schule", "hausaufgaben", "freund", "fahrrad", "tasche", "handy"],
    "Spiele": ["minecraft", "godofwar", "fortnite", "zelda", "cyberpunk"],
    "Tiere": ["elefant", "löwe".replace("ß", "ss"), "giraffe", "pinguin", "kaninchen"],
}

# Buchstaben (inkl. Umlaute)
LETTERS = list("abcdefghijklmnopqrstuvwxyz") + ["ä", "ö", "ü"]

MAX_ERRORS = 6

# -----------------------
# Hilfsfunktionen: Sound
# -----------------------

def load_sound(name):
    path = os.path.join(SOUNDS_DIR, name)
    if os.path.exists(path):
        try:
            return pygame.mixer.Sound(path)
        except Exception as e:
            print("Sound-Ladefehler:", e)
            return None
    return None

SOUND_CORRECT = load_sound("success.wav")
SOUND_WRONG = load_sound("failed.wav")
SOUND_WIN = load_sound("win.wav")
SOUND_LOSE = load_sound("lost.wav")

def play_sound(sound, volume=0.6):
    if not sound:
        return
    try:
        sound.set_volume(volume)
        sound.play()
    except Exception as e:
        print("Play sound error:", e)

# -----------------------
# Highscore Funktionen
# -----------------------
def load_scores():
    if not os.path.exists(SCORES_FILE):
        return []
    try:
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_scores(scores):
    try:
        with open(SCORES_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Error saving scores:", e)

def add_score(name, category, word, wrong_guesses):
    scores = load_scores()
    entry = {
        "name": name,
        "category": category,
        "word": word,
        "wrong": wrong_guesses
    }
    scores.append(entry)
    # einfache Sortierung nach wenigen Fehlern (besser = weniger wrong)
    scores = sorted(scores, key=lambda e: (e["wrong"], e["name"]))[:50]  # begrenzen
    save_scores(scores)

# -----------------------
# Haupt-App Klasse
# -----------------------
class HangmanApp:
    def __init__(self, root):
        self.root = root
        root.title(APP_TITLE)
        self.fullscreen = False
        self.sound_volume = 0.6

        # zentrieren
        self.center_window(1000, 700)

        # Frames
        self.menu_frame = tk.Frame(root, bg="#f0f0f0")
        self.game_frame = tk.Frame(root, bg="#fafafa")
        self.settings_frame = None

        # Spielzustand
        self.category = None
        self.word = ""
        self.guessed = set()
        self.errors = 0

        # GUI-Elemente die wiederverwendet werden
        self.canvas = None
        self.word_label = None
        self.guessed_label = None
        self.keyboard_buttons = {}
        self.entry_guess = None

        self.build_menu()

    # Fenster zentrieren
    def center_window(self, w, h):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # --------------
    # Menü
    # --------------
    def build_menu(self):
        self.clear_frames()
        self.menu_frame.pack(expand=True, fill="both")

        title = tk.Label(self.menu_frame, text="Willkommen", font=("Arial", 36), bg="#f0f0f0")
        title.pack(pady=40)

        btn_play = tk.Button(self.menu_frame, text="Spiel starten", font=("Arial", 18), width=20, command=self.menu_start)
        btn_play.pack(pady=10)

        btn_settings = tk.Button(self.menu_frame, text="Einstellungen", font=("Arial", 16), width=20, command=self.menu_settings)
        btn_settings.pack(pady=6)

        btn_scores = tk.Button(self.menu_frame, text="Highscores", font=("Arial", 16), width=20, command=self.menu_scores)
        btn_scores.pack(pady=6)

        btn_quit = tk.Button(self.menu_frame, text="Beenden", font=("Arial", 16), width=20, command=self.root.destroy)
        btn_quit.pack(pady=6)

    # --------------
    # Spiel starten: Kategorie wählen
    # --------------
    def menu_start(self):
        # Dialog: Kategorie wählen oder neue erstellen
        cats = list(CATEGORIES.keys())
        dialog = simpledialog.askstring("Kategorie", f"Wähle Kategorie ({', '.join(cats)}) oder gib neuen Namen ein:")
        if dialog is None:
            return
        chosen = dialog.strip()
        if chosen == "":
            return
        # Wenn neue Kategorie -> anlegen
        if chosen not in CATEGORIES:
            CATEGORIES[chosen] = []
        self.category = chosen
        # Neues Spiel initialisieren
        self.start_game()

    # --------------
    # Einstellungen
    # --------------
    def menu_settings(self):
        # Einfacher Einstellungsdialog: Vollbild, Lautstärke
        dlg = tk.Toplevel(self.root)
        dlg.title("Einstellungen")
        dlg.geometry("400x220")
        dlg.transient(self.root)

        tk.Label(dlg, text="Vollbild (True/False):").pack(pady=6)
        fs_var = tk.StringVar(value=str(self.fullscreen))
        fs_entry = tk.Entry(dlg, textvariable=fs_var)
        fs_entry.pack()

        tk.Label(dlg, text="Lautstärke (0.0 - 1.0):").pack(pady=6)
        vol_var = tk.DoubleVar(value=self.sound_volume)
        vol_scale = tk.Scale(dlg, variable=vol_var, from_=0.0, to=1.0, resolution=0.05, orient="horizontal", length=250)
        vol_scale.pack()

        def save_and_close():
            val = fs_var.get().lower()
            self.fullscreen = (val in ("true", "1", "yes", "y"))
            self.root.attributes("-fullscreen", self.fullscreen)
            self.sound_volume = max(0.0, min(1.0, vol_var.get()))
            dlg.destroy()

        tk.Button(dlg, text="Speichern", command=save_and_close).pack(pady=8)

    # --------------
    # Highscores anzeigen
    # --------------
    def menu_scores(self):
        scores = load_scores()
        dlg = tk.Toplevel(self.root)
        dlg.title("Highscores")
        dlg.geometry("500x400")
        dlg.transient(self.root)
        frame = tk.Frame(dlg)
        frame.pack(expand=True, fill="both", padx=8, pady=8)
        if not scores:
            tk.Label(frame, text="Noch keine Highscores vorhanden.").pack()
            return
        # einfache Anzeige
        for i, s in enumerate(scores[:50], start=1):
            txt = f"{i}. {s['name']} - {s['category']} - {s['word']} (Fehler: {s['wrong']})"
            tk.Label(frame, text=txt, anchor="w").pack(fill="x")

    # --------------
    # Spiel-Aufbau
    # --------------
    def start_game(self):
        self.clear_frames()
        self.game_frame.pack(expand=True, fill="both")

        # Zufallswort aus Kategorie (falls leer -> Dialog zum Hinzufügen)
        wordlist = CATEGORIES.get(self.category, [])
        if not wordlist:
            ans = simpledialog.askstring("Kategorie leer", "Kategorie leer. Gib ein Wort ein, das hinzugefügt werden soll:")
            if not ans:
                self.build_menu()
                return
            wordlist.append(ans.strip().lower())
            CATEGORIES[self.category] = wordlist

        self.word = random.choice(wordlist).lower()
        self.guessed = set()
        self.errors = 0

        # Layout: Canvas links, Mitte Wort, rechts Info
        left = tk.Frame(self.game_frame)
        left.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        center = tk.Frame(self.game_frame)
        center.grid(row=0, column=1, padx=10, pady=10)

        right = tk.Frame(self.game_frame)
        right.grid(row=0, column=2, padx=10, pady=10, sticky="ne")

        # Canvas für Hangman
        self.canvas = tk.Canvas(left, width=420, height=520, bg="white")
        self.canvas.pack()

        # Wortanzeige
        self.word_label = tk.Label(center, text="", font=("Arial", 36))
        self.word_label.pack(pady=20)

        # Eingabe für ganzes Wort
        entry_frame = tk.Frame(center)
        entry_frame.pack(pady=6)
        self.entry_guess = tk.Entry(entry_frame, font=("Arial", 14), width=18)
        self.entry_guess.grid(row=0, column=0, padx=6)
        tk.Button(entry_frame, text="prüfen", command=self.try_full_word).grid(row=0, column=1, padx=4)

        # virtuelle Tastatur
        kb = tk.Frame(center)
        kb.pack(pady=8)
        self.keyboard_buttons = {}
        r = 0; c = 0
        for ch in LETTERS:
            b = tk.Button(kb, text=ch.upper(), width=4, height=2, command=lambda ch=ch: self.on_letter(ch))
            b.grid(row=r, column=c, padx=2, pady=2)
            self.keyboard_buttons[ch] = b
            c += 1
            if c % 10 == 0:
                r += 1; c = 0

        # Rechts: geraten + Aktionen
        tk.Label(right, text="Bereits geraten:", font=("Arial", 14)).pack(anchor="ne")
        self.guessed_label = tk.Label(right, text="", font=("Arial", 14))
        self.guessed_label.pack(anchor="ne", pady=6)
        tk.Button(right, text="Wort anzeigen", command=self.reveal_word).pack(pady=6)
        tk.Button(right, text="Neues Wort hinzufügen (Kategorie)", command=self.add_word_dialog).pack(pady=6)
        tk.Button(right, text="Menu", command=self.build_menu).pack(pady=6)

        self.update_display()

    # --------------
    # Gameplay Methoden
    # --------------
    def on_letter(self, ch):
        if ch in self.guessed:
            return
        self.guessed.add(ch)
        # deaktivieren Button
        btn = self.keyboard_buttons.get(ch)
        if btn:
            btn.config(state="disabled")
        if ch in self.word:
            play_sound(SOUND_CORRECT, self.sound_volume)
        else:
            self.errors += 1
            play_sound(SOUND_WRONG, self.sound_volume)
        self.update_display()
        self.check_end()

    def try_full_word(self):
        guess = self.entry_guess.get().strip().lower()
        self.entry_guess.delete(0, tk.END)
        if not guess:
            return
        if guess == self.word:
            # gewinn
            self.guessed.update(set(self.word))
            play_sound(SOUND_WIN, self.sound_volume)
            self.update_display()
            self.end_game(win=True)
        else:
            self.errors += 1
            play_sound(SOUND_WRONG, self.sound_volume)
            self.update_display()
            self.check_end()

    def update_display(self):
        # Wort anzeigen
        shown = " ".join([c if c in self.guessed else "•" for c in self.word])
        self.word_label.config(text=shown)
        # geraten
        self.guessed_label.config(text=" ".join(sorted(self.guessed)))
        # Hangman zeichnen
        self.draw_hangman()

    def draw_hangman(self):
        c = self.canvas
        c.delete("all")
        # Boden und Galgen
        c.create_line(50,480,370,480, width=4)   # Boden
        c.create_line(110,480,110,60, width=6)   # Pfosten
        c.create_line(110,60,260,60, width=6)    # Balken
        c.create_line(260,60,260,110, width=4)   # Seil
        # Körperteile nach Fehleranzahl
        if self.errors >= 1:
            c.create_oval(230,110,290,170, width=3)  # Kopf
        if self.errors >= 2:
            c.create_line(260,170,260,260, width=3)  # Körper
        if self.errors >= 3:
            c.create_line(260,190,220,230, width=3)  # Arm links
        if self.errors >= 4:
            c.create_line(260,190,300,230, width=3)  # Arm rechts
        if self.errors >= 5:
            c.create_line(260,260,230,320, width=3)  # Bein links
        if self.errors >= 6:
            c.create_line(260,260,290,320, width=3)  # Bein rechts

        # option: kleine Hinweise
        c.create_text(210,20, text=f"Kategorie: {self.category}", anchor="w", font=("Arial", 12))

    def check_end(self):
        if all(ch in self.guessed for ch in self.word):
            play_sound(SOUND_WIN, self.sound_volume)
            self.end_game(win=True)
        elif self.errors >= MAX_ERRORS:
            play_sound(SOUND_LOSE, self.sound_volume)
            self.end_game(win=False)

    def end_game(self, win=False):
        # Namen abfragen und in Highscores speichern
        if win:
            msg = f"Gewonnen! Wort: {self.word}"
        else:
            msg = f"Verloren! Wort: {self.word}"
        name = simpledialog.askstring("Spiel beendet", f"{msg}\nDein Name für Highscore (leer = nicht speichern):")
        wrongs = self.errors
        if name:
            add_score(name.strip(), self.category or "?", self.word, wrongs)
        # zurück ins Menü
        self.build_menu()

    # --------------
    # Utility Methoden
    # --------------
    def reveal_word(self):
        messagebox.showinfo("Wort", f"Das Wort ist: {self.word}")

    def add_word_dialog(self):
        s = simpledialog.askstring("Wort hinzufügen", "Gib ein Wort ein (wird zur Kategorie hinzugefügt):")
        if not s:
            return
        s = s.strip().lower()
        if s:
            CATEGORIES.setdefault(self.category, []).append(s)
            messagebox.showinfo("Hinzugefügt", f"Das Wort '{s}' wurde zur Kategorie '{self.category}' hinzugefügt.")

    def clear_frames(self):
        for f in (self.menu_frame, self.game_frame):
            for w in f.winfo_children():
                w.destroy()
            f.pack_forget()

# -----------------------
# Start der App
# -----------------------
def main():
    root = tk.Tk()
    app = HangmanApp(root)
    pygame.mixer.init()

    # ESC schliesst, falls Vollbild aktiv (freundlich)
    def on_escape(event=None):
        if app.fullscreen:
            app.fullscreen = False
            root.attributes("-fullscreen", False)
        else:
            # falls nicht fullscreen -> schliessen
            root.destroy()

    root.bind_all("<Escape>", on_escape)

    root.mainloop()

if __name__ == "__main__":
    main()
    