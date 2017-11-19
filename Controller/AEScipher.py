from Cryptodome.Cipher import AES
from Cryptodome import Random
import ast

class AEScipher:

    # Constructor for Encryption and Decryption
    def __init__(self):
        self.s_key = b'\x07\xb4t\xa6\rsZ\x89I=f\xec\xe0?\xfa\x90\xa8\xb0\xa9\xdd\x8f\xfd\xef\x10\xeah\xa1\xe3\xc9z\xeb\xf6'
        # self.s_key = Random.new().read(32)
        self.BS = AES.block_size

    # Encrypt the data
    def encrypt(self, plain):
        plain = str(plain)
        plain = self.pad(plain.encode())
        iv = Random.new().read(self.BS)
        cipher = AES.new(self.s_key, AES.MODE_CBC, iv)
        return (iv + cipher.encrypt(plain))

    # decrypt the data
    def decrypt(self, e):
        iv = e[:self.BS]
        cipher = AES.new(self.s_key, AES.MODE_CBC, iv)
        code = self.unpad(cipher.decrypt(e[self.BS:])).decode()
        return ast.literal_eval(code)

    # pat data
    def pad(self, m):
        BS = self.BS
        return m + bytes([BS - len(m) % BS] * (BS - len(m) % BS))

    # unpad data
    def unpad(self, m):
        return m[:-int(m[-1])]
