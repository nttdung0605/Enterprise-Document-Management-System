from Crypto.Cipher import AES
from Crypto.Util.Padding import (
    pad,
    unpad
)

import os

AES_KEY = (
    b"12345678901234567890123456789012"
)

def encrypt_data(data):

    iv = os.urandom(16)

    cipher = AES.new(
        AES_KEY,
        AES.MODE_CBC,
        iv
    )

    encrypted = cipher.encrypt(
        pad(
            data,
            AES.block_size
        )
    )

    return iv + encrypted

def decrypt_data(data):

    iv = data[:16]

    encrypted = data[16:]

    cipher = AES.new(
        AES_KEY,
        AES.MODE_CBC,
        iv
    )

    return unpad(
        cipher.decrypt(
            encrypted
        ),
        AES.block_size
    )