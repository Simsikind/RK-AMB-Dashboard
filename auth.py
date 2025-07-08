#file: auth.py

import os, base64, hashlib
from cryptography.fernet import Fernet
from tkinter import Tk, simpledialog, messagebox
import os
import datetime
import getpass
import socket

PIN_FILE = ".pinfile"
VERIFICATION_STRING = b"AMBULANZ-VERIFIZIERUNG"

def derive_key(pin: str, salt: bytes) -> bytes:
    key = hashlib.pbkdf2_hmac('sha256', pin.encode(), salt, 100_000)
    return base64.urlsafe_b64encode(key)

def setup_pin():
    root = Tk()
    root.withdraw()
    pin = simpledialog.askstring("neuen PIN setzen", "Bitte 4- bis 8-stelligen PIN eingeben:", show="*")
    if not pin or not pin.isdigit() or not (4 <= len(pin) <= 8):
        messagebox.showerror("Fehler", "Ungültiger PIN.")
        exit()

    salt = os.urandom(16)
    key = derive_key(pin, salt)
    fernet = Fernet(key)
    token = fernet.encrypt(VERIFICATION_STRING)

    with open(PIN_FILE, "wb") as f:
        f.write(salt + b":" + token)

    messagebox.showinfo("neuen PIN gesetzt", "PIN wurde erfolgreich gespeichert.")

def load_key_with_pin() -> Fernet:
    if not os.path.exists(PIN_FILE):
        setup_pin()

    with open(PIN_FILE, "rb") as f:
        content = f.read()
        salt, token = content.split(b":", 1)

    root = Tk()
    root.withdraw()
    pin = simpledialog.askstring("PIN eingeben", "Bitte PIN eingeben:", show="*")
    if not pin:
        exit()

    key = derive_key(pin, salt)
    fernet = Fernet(key)

    try:
        if fernet.decrypt(token) != VERIFICATION_STRING:
            raise ValueError("PIN falsch.")
    except Exception as e:
        messagebox.showerror("Fehler", "PIN ungültig oder Datei beschädigt.")
        exit()

    return fernet

def rekey_file(filepath: str, old_fernet: Fernet, new_fernet: Fernet):
    """
    Entschlüsselt eine Datei mit dem alten Schlüssel und verschlüsselt sie mit dem neuen.
    """
    try:
        with open(filepath, "rb") as f:
            encrypted = f.read()
            decrypted = old_fernet.decrypt(encrypted)

        with open(filepath, "wb") as f:
            f.write(new_fernet.encrypt(decrypted))

        print(f"Datei neu verschlüsselt mit neuem Schlüssel: {filepath}")

    except Exception as e:
        print(f"Fehler beim Rekeyen von {filepath}: {e}")

def log(message: str, Ambnum: str = "Unbekannt"):
    """
    Protokolliert eine Nachricht mit Zeitstempel, Benutzername und IP-Adresse
    in die Datei log/<Ambnum>.log.

    :param message: Die zu protokollierende Nachricht
    :param Ambnum: Die Ambulanznummer zur Zuordnung der Logdatei
    """
    # Zielverzeichnis und Datei
    log_dir = "log"
    # Nur Ziffern aus Ambnum extrahieren
    ambnum_digits = ''.join(filter(str.isdigit, Ambnum))
    log_file = os.path.join(log_dir, f"{ambnum_digits}.log")
    
    # Verzeichnisse erstellen, falls nicht vorhanden
    os.makedirs(log_dir, exist_ok=True)

    # Zeit, Benutzer, IP-Adresse
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    username = getpass.getuser()
    
    try:
        ip_address = socket.gethostbyname(socket.gethostname())
    except:
        ip_address = "Unbekannt"

    # Log-Zeile zusammenbauen
    log_entry = f"[{timestamp}] {username} ({ip_address}): {message}\n"

    # In Datei schreiben (falls nicht vorhanden, wird sie automatisch erstellt)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)
    
    print("[LOG]:", log_entry)


