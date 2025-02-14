import tkinter as tk
from tkinter import scrolledtext

def send_message():
    message = entry_field.get()
    if message.strip():  
        chat_display.insert(tk.END, f"You: {message}\n")
        entry_field.delete(0, tk.END)  
        chat_display.yview(tk.END)  


root = tk.Tk()
root.title("Chatbox")
root.geometry("800x500")


chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='normal', width=100, height=30)
chat_display.pack(pady=10, padx=10)

entry_field = tk.Entry(root, width=70)
entry_field.pack(pady=5)

send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack(pady=5)

root.mainloop()
