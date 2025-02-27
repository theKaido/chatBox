import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import date, datetime

username = ""
password = ""
history= "history.txt"


#AUTHENTIFACTION WINDOW
def authenticate():
    global username, password
    auth_window = tk.Toplevel(root)
    auth_window.title("Authentification")
    auth_window.geometry("300x200")

    tk.Label(auth_window, text="Nom d'utilisateur:").pack(pady=5)
    username_entry = tk.Entry(auth_window)
    username_entry.pack(pady=5)

    tk.Label(auth_window, text="Clé :" ).pack(pady=5)
    password_entry= tk.Entry(auth_window, show='*')
    password_entry.pack(pady=5)

    def submit(user, keys):
        global username, password
        if user and keys:
            username = user
            password = keys
            auth_window.destroy()
        else:
            messagebox.showerror("Erreur", "Veuillez entrer un nom d'utilisateur !")

    submit_button = tk.Button(auth_window, text="Valider", command=lambda: submit(username_entry.get(), password_entry.get()))
    submit_button.pack(pady=10)

    root.wait_window(auth_window)

#FUNCTIONALITY
def send_message(event=None):
    global username, password
    message = entry_field.get().strip()
    if message.strip():
        timestamp = datetime.now().strftime("%d/%m/%Y - %H:%M")
        formatted_message = f"{username}[{timestamp}]: {message}\n"
        chat_display.insert(tk.END, formatted_message)
        entry_field.delete(0, tk.END)
        chat_display.yview(tk.END)

        save_chat(formatted_message)

def save_chat(message):
    with open(history, "a", encoding="utf-8") as file:
        file.write(message)

def load_chat():
    with open(history, "r", encoding="utf-8") as file:
        if file:
            chat_history = file.read()
            chat_display.insert(tk.END, chat_history)
            chat_display.yview(tk.END)
        else:
            pass

#MAIN WINDOWS
root = tk.Tk()
root.title("Chatbox")
root.geometry("800x500")


authenticate()

chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='normal', width=100, height=30)
chat_display.pack(pady=10, padx=10)

load_chat()

entry_field = tk.Entry(root, width=70)
entry_field.pack(pady=5)
entry_field.bind("<Return>",send_message)

send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack(pady=5)

root.mainloop()

