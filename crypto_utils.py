# crypto_utils.py
# 暗号化と復号化のユーティリティモジュール

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

def derive_key(password: str, salt: bytes, iterations: int = 100_000) -> bytes:
    """
    パスワードから鍵を生成する関数（PBKDF2 + SHA256）
    saltはランダムなバイト列（解凍時にも必要）
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # AES256の鍵長
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    return key

def encrypt(data: bytes, password: str) -> bytes:
    """
    AES-256-CBCで暗号化。返り値は
    salt(16バイト) + iv(16バイト) + ciphertext
    のバイト列になる。
    """
    salt = os.urandom(16)
    key = derive_key(password, salt)

    iv = os.urandom(16)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    return salt + iv + ciphertext

def decrypt(enc_data: bytes, password: str) -> bytes:
    """
    暗号化データを復号化する関数。
    enc_dataはsalt(16バイト) + iv(16バイト) + ciphertextの構成。
    """
    salt = enc_data[:16]
    iv = enc_data[16:32]
    ciphertext = enc_data[32:]
    key = derive_key(password, salt)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()

    return data
