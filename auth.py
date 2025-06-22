import os, base64, hashlib
from cryptography.fernet import Fernet
from tkinter import Tk, simpledialog, messagebox

PIN_FILE = ".pinfile"
VERIFICATION_STRING = b"AMBULANZ-VERIFIZIERUNG"

def derive_key(pin: str, salt: bytes) -> bytes:
    key = hashlib.pbkdf2_hmac('sha256', pin.encode(), salt, 100_000)
    return base64.urlsafe_b64encode(key)

def setup_pin():
    root = Tk()
    root.withdraw()
    pin = simpledialog.askstring("PIN setzen", "Bitte 4- bis 8-stelligen PIN eingeben:", show="*")
    if not pin or not pin.isdigit() or not (4 <= len(pin) <= 8):
        messagebox.showerror("Fehler", "Ungültiger PIN.")
        exit()

    salt = os.urandom(16)
    key = derive_key(pin, salt)
    fernet = Fernet(key)
    token = fernet.encrypt(VERIFICATION_STRING)

    with open(PIN_FILE, "wb") as f:
        f.write(salt + b":" + token)

    messagebox.showinfo("PIN gesetzt", "PIN wurde erfolgreich gespeichert.")

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

