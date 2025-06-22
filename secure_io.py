import pickle
from cryptography.fernet import Fernet

def write_encrypted(filepath: str, data, fernet: Fernet):
    with open(filepath, "wb") as f:
        encrypted = fernet.encrypt(pickle.dumps(data))
        f.write(encrypted)
        print("Verschlüsselte Datei geschrieben")

def read_encrypted(filepath: str, fernet: Fernet):
    with open(filepath, "rb") as f:
        decrypted = fernet.decrypt(f.read())
        print("verschlüsselte Datei gelesen")
        return pickle.loads(decrypted)
        

def encrypt_existing_file(filepath: str, fernet: Fernet):
    with open(filepath, "rb") as f:
        data = pickle.load(f)
    with open(filepath, "wb") as f:
        f.write(fernet.encrypt(pickle.dumps(data)))
        print("Datei verschlüsselt")
