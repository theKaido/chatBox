import tkinter as tk
from Client import *
from tkinter import scrolledtext, messagebox
from datetime import date, datetime
import os
import threading

username = ""
host = ""
port = ""
history= "history.txt"
client = None




#AUTHENTIFACTION WINDOW
def authenticate():
    global username, host, port
    auth_window = tk.Toplevel(root)
    auth_window.title("Authentification")
    auth_window.geometry("300x200")

    tk.Label(auth_window, text="Nom d'utilisateur:").pack(pady=5)
    username_entry = tk.Entry(auth_window)
    username_entry.pack(pady=5)

    tk.Label(auth_window, text="Hôte:").pack(pady=5)
    host_entry = tk.Entry(auth_window)
    host_entry.pack(pady=5)

    tk.Label(auth_window, text="Port:").pack(pady=5)
    port_entry = tk.Entry(auth_window)
    port_entry.pack(pady=5)

    def submit(user, hoste, porte):
        global username, host, port, client
        if user and hoste and porte and porte.isdigit():
            username = user
            host = hoste
            port = porte
            auth_window.destroy()
        else:
            messagebox.showerror("Erreur", "Invalid entries, please verify...")

    submit_button = tk.Button(auth_window, text="Valider", command=lambda: submit(username_entry.get(), host_entry.get(), port_entry.get()))
    submit_button.pack(pady=10)

    root.wait_window(auth_window)

#FUNCTIONALITY
def send_message(event=None):
    global username, client
    message = entry_field.get().strip()
    if message.strip():
        timestamp = datetime.now().strftime("%d/%m/%Y - %H:%M")
        formatted_message = f"{username}[{timestamp}]: {message}\n"
        chat_display.insert(tk.END, formatted_message)
        entry_field.delete(0, tk.END)
        chat_display.yview(tk.END)
        save_chat(formatted_message)
        client.send_msg(username, message)

def save_chat(message):
    with open(history, "a", encoding="utf-8") as file:
        file.write(message)

def load_chat():
    if not os.path.exists(history):
        with open(history, "w", encoding="utf-8") as file:
            pass

    with open(history, "r", encoding="utf-8") as file:
        chat_history = file.read()
        chat_display.insert(tk.END, chat_history)
        chat_display.yview(tk.END)

def clear_chat():
    confirm = messagebox.askyesno("Confirmation","Voulez-vous vraiment effacer l'historique du chat ?")
    if confirm:
        chat_display.delete('1.0', tk.END)
        open(history, "w").close()
        messagebox.showinfo("Succès","Historique du chat effacé.")



#MAIN WINDOWS
root = tk.Tk()
root.title("Chatbox")
root.geometry("800x500")


authenticate()

chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='normal', width=100, height=30)
chat_display.pack(pady=10, padx=10)
#chat_display.config(state=tk.DISABLED)

def add_message(user, msg):
    global chat_display
    timestamp = datetime.now().strftime("%d/%m/%Y - %H:%M")
    formatted_message = f"{user}[{timestamp}]: {msg}\n"
    chat_display.insert(tk.END, formatted_message)
    entry_field.delete(0, tk.END)
    chat_display.yview(tk.END)

load_chat()

chat_display.insert(tk.END, "==========================")

client = Client(host, int(port))
client.init_routine(add_message)

entry_field = tk.Entry(root, width=70)
entry_field.pack(pady=5)
entry_field.bind("<Return>",send_message)

button_frame = tk.Frame(root)
button_frame.pack(pady=5)

send_button = tk.Button(button_frame, text="Envoyer", command=send_message)
send_button.grid(row=0, column=0, padx=5)

clear_button = tk.Button(button_frame, text="Effacer l'historique", command=clear_chat)
clear_button.grid(row=0, column=1, padx=5)



root.mainloop()
