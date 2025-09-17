import tkinter as tk

# Window setup
def on_escape(event=None):
    root.destroy()
root = tk.Tk()
root.title("Hangman Minigame")
root.attributes("-fullscreen",True)
root.configure(bg="#869fb3")
root.bind_all("<Escape>",on_escape)
root.resizable(False,False)

#Button erstellen

def buttonpress():
    label = tk.Label(root, text="Du hast mich gedrückt!", font=("arial", 16))
    label.place(x=680, y=10)

button = tk.Button(
    root,
    text="Klick mich!",
    font=("arial", 20),
    bg="#869fb3",
    command=buttonpress
)
button.place(x=700, y=450)


#Screens


root.mainloop()
