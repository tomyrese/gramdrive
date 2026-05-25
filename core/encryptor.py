import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

class Encryptor:
    @staticmethod
    def derive_key(passphrase: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        return kdf.derive(passphrase.encode())

    @classmethod
    def encrypt_file(cls, input_path: str, output_path: str, passphrase: str) -> None:
        salt = os.urandom(16)
        iv = os.urandom(16)
        key = cls.derive_key(passphrase, salt)
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        padder = PKCS7(128).padder()

        with open(input_path, "rb") as f_in, open(output_path, "wb") as f_out:
            f_out.write(salt)
            f_out.write(iv)
            
            while True:
                chunk = f_in.read(64 * 1024)
                if not chunk:
                    break
                padded_chunk = padder.update(chunk)
                if padded_chunk:
                    f_out.write(encryptor.update(padded_chunk))
            
            f_out.write(encryptor.update(padder.finalize()))
            f_out.write(encryptor.finalize())

    @classmethod
    def decrypt_file(cls, input_path: str, output_path: str, passphrase: str) -> None:
        with open(input_path, "rb") as f_in:
            salt = f_in.read(16)
            iv = f_in.read(16)
            
            key = cls.derive_key(passphrase, salt)
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            decryptor = cipher.decryptor()
            unpadder = PKCS7(128).unpadder()
            
            with open(output_path, "wb") as f_out:
                while True:
                    chunk = f_in.read(64 * 1024)
                    if not chunk:
                        break
                    decrypted_chunk = decryptor.update(chunk)
                    if decrypted_chunk:
                        f_out.write(unpadder.update(decrypted_chunk))
                
                final_decrypted = decryptor.finalize()
                f_out.write(unpadder.update(final_decrypted))
                f_out.write(unpadder.finalize())
