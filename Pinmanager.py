import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import auth
import os
from cryptography.fernet import Fernet

fernet_global = None
old_fernet = None
new_fernet = None

# Hauptfenster
root = tk.Tk()
root.title("PIN-Verwaltung")
root.geometry("400x250")
root.resizable(False, False)

# ------------------- Funktionen -------------------

def set_new_pin():
    if os.path.exists(auth.PIN_FILE):
        if not messagebox.askyesno("PIN überschreiben?", "Es existiert bereits ein PIN. Möchtest du ihn wirklich überschreiben?"):
            return
    auth.setup_pin()

def test_pin():
    try:
        f = auth.load_key_with_pin()
        messagebox.showinfo("Erfolg", "PIN war korrekt.")
    except Exception as e:
        messagebox.showerror("Fehler", f"PIN ungültig: {e}")

def rekey_file_gui():
    global old_fernet, new_fernet
    messagebox.showinfo("Alter Schlüssel", "Bitte gib den alten PIN ein.")
    old_fernet = auth.load_key_with_pin()

    messagebox.showinfo("Neuer Schlüssel", "Jetzt neuen PIN setzen.")
    auth.setup_pin()
    new_fernet = auth.load_key_with_pin()

    filepath = filedialog.askopenfilename(title="Wähle .ambdat Datei", filetypes=[("Ambulanzdateien", "*.ambdat")])
    if not filepath:
        return

    try:
        auth.rekey_file(filepath, old_fernet, new_fernet)
        messagebox.showinfo("Erfolg", "Datei wurde neu verschlüsselt.")
    except Exception as e:
        messagebox.showerror("Fehler", f"Rekey fehlgeschlagen: {e}")

# ------------------- GUI Elemente -------------------

label = tk.Label(root, text="Wähle eine Option zur PIN-Verwaltung:", font=("Helvetica", 12))
label.pack(pady=10)

btn_set = tk.Button(root, text="Neuen PIN setzen", command=set_new_pin, width=30)
btn_set.pack(pady=5)

btn_test = tk.Button(root, text="PIN testen", command=test_pin, width=30)
btn_test.pack(pady=5)

btn_rekey = tk.Button(root, text="Datei neu verschlüsseln (Rekey)", command=rekey_file_gui, width=30)
btn_rekey.pack(pady=5)

btn_close = tk.Button(root, text="Schließen", command=root.destroy, width=30)
btn_close.pack(pady=20)

# ------------------- Main Loop -------------------

root.mainloop()
