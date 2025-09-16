import tkinter as tk

# Window setup
def on_escape(event=None):
    root.destroy()
root = tk.Tk()
root.title("Hangman Minigame")
root.attributes("-fullscreen",True)
root.configure(bg="beige")
root.bind_all("<Escape>",on_escape)
root.resizable(False,False)
root.mainloop()