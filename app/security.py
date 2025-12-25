from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

KEY_FILE = "aes.key"

# Generate/load persistent AES key
if not os.path.exists(KEY_FILE):
    with open(KEY_FILE, "wb") as f:
        f.write(os.urandom(32))

with open(KEY_FILE, "rb") as f:
    KEY = f.read()

backend = default_backend()

def encrypt_file(input_path: str, output_path: str):
    nonce = os.urandom(12)  # 12 bytes for GCM nonce
    cipher = Cipher(algorithms.AES(KEY), modes.GCM(nonce), backend=backend)
    encryptor = cipher.encryptor()

    with open(input_path, "rb") as f_in:
        plaintext = f_in.read()

    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    with open(output_path, "wb") as f_out:
        f_out.write(nonce)        # first 12 bytes = nonce
        f_out.write(ciphertext)   # ciphertext
        f_out.write(encryptor.tag)  # last 16 bytes = tag


def decrypt_file(input_path: str, output_path: str):
    with open(input_path, "rb") as f_in:
        file_content = f_in.read()

    nonce = file_content[:12]       # first 12 bytes
    tag = file_content[-16:]        # last 16 bytes
    ciphertext = file_content[12:-16]  # middle = ciphertext

    cipher = Cipher(algorithms.AES(KEY), modes.GCM(nonce, tag), backend=backend)
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    with open(output_path, "wb") as f_out:
        f_out.write(plaintext)
