import tkinter as tk
from tkinter import scrolledtext, messagebox
from Client import *
from datetime import datetime
import os

# === Variables globales ===
username = ""
host = ""
port = ""
history = "history.txt"
client = None


# === Fenêtre d'authentification ===
def show_auth_window():
    global username, host, port
    auth = tk.Toplevel(root)
    auth.title("Authentification")
    auth.geometry("300x320")
    auth.resizable(False, False)

    tk.Label(auth, text="Nom d'utilisateur :").pack(pady=(10, 0))
    username_entry = tk.Entry(auth)
    username_entry.pack(pady=5)
    username_entry.focus()

    tk.Label(auth, text="Hôte :").pack()
    host_entry = tk.Entry(auth)
    host_entry.pack(pady=5)

    tk.Label(auth, text="Port :").pack()
    port_entry = tk.Entry(auth)
    port_entry.pack(pady=5)

    def submit():
        nonlocal username_entry, host_entry, port_entry
        u, h, p = username_entry.get(), host_entry.get(), port_entry.get()
        if u and h and p.isdigit():
            # mise à jour globale
            nonlocal auth
            global username, host, port
            username, host, port = u, h, int(p)
            auth.destroy()
        else:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs correctement.")

    tk.Button(auth, text="Se connecter", command=submit).pack(pady=10)
    root.wait_window(auth)


# === Gestion du chat ===
def send_message(event=None):
    message = entry_field.get().strip()
    if message:
        timestamp = datetime.now().strftime("%d/%m/%Y - %H:%M")
        msg = f"{username}[{timestamp}]: {message}\n"
        chat_display.insert(tk.END, msg)
        chat_display.yview(tk.END)
        entry_field.delete(0, tk.END)
        save_chat(msg)
        try:
            client.send_msg(username, message)
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de l'envoi : {e}")

def add_message(sender, msg):
    timestamp = datetime.now().strftime("%d/%m/%Y - %H:%M")
    formatted = f"{sender}[{timestamp}]: {msg}\n"
    chat_display.insert(tk.END, formatted)
    chat_display.yview(tk.END)

def save_chat(message):
    with open(history, "a", encoding="utf-8") as file:
        file.write(message)

def load_chat():
    if os.path.exists(history):
        with open(history, "r", encoding="utf-8") as file:
            chat_display.insert(tk.END, file.read())
            chat_display.insert(tk.END, "\n==========================\n")
            chat_display.yview(tk.END)

def clear_chat():
    if messagebox.askyesno("Confirmation", "Effacer l'historique du chat ?"):
        open(history, "w", encoding="utf-8").close()
        chat_display.delete('1.0', tk.END)
        messagebox.showinfo("Succès", "Historique effacé.")

def close_app():
    try:
        client.close()
    except:
        pass
    root.destroy()


# === Interface principale ===
root = tk.Tk()
root.title("Chat sécurisé")
root.geometry("800x500")
root.configure(bg="#f0f0f0")
root.protocol("WM_DELETE_WINDOW", close_app)

show_auth_window()

chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=25, font=("Helvetica", 10))
chat_display.pack(padx=10, pady=(10, 5))
chat_display.config(state=tk.NORMAL)

entry_field = tk.Entry(root, width=80, font=("Helvetica", 10))
entry_field.pack(pady=5)
entry_field.bind("<Return>", send_message)

button_frame = tk.Frame(root, bg="#f0f0f0")
button_frame.pack(pady=5)

default_btn_style = {
    "font": ("Helvetica", 11),
    "bg": "#e8e8e8",   # gris clair typique mac
    "activebackground": "#d0d0d0",
    "bd": 0,            # aucune bordure
    "relief": "flat",
    "highlightthickness": 0,
    "cursor": "hand2"
}

send_btn = tk.Button(button_frame, text="Envoyer", command=send_message, **default_btn_style)
send_btn.grid(row=0, column=0, padx=5)

clear_btn = tk.Button(button_frame, text="Effacer historique", command=clear_chat, **default_btn_style)
clear_btn.grid(row=0, column=1, padx=5)


# === Lancement du client et chargement du chat ===
load_chat()
try:
    client = Client(host, port)
    client.init_routine(add_message)
except Exception as e:
    messagebox.showerror("Erreur de connexion", f"Impossible de se connecter au serveur :\n{e}")
    root.destroy()

root.mainloop()
