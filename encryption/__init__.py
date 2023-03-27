try:
    from cryptography.fernet import Fernet
    from argon2.low_level import hash_secret_raw, Type
    import base64
except:
    from pyntree.errors import Error
    raise Error.EncryptionNotAvailable()


def derive_key(password: str, salt: bytes):
    password = password.encode()
    key = hash_secret_raw(
        password,
        salt,
        time_cost=1,
        memory_cost=8,
        parallelism=1,
        hash_len=32,
        type=Type.D
    )
    key = base64.urlsafe_b64encode(key[:32])
    return key


def encrypt(data: bytes, password: str, salt: bytes):
    key = derive_key(password, salt)
    f = Fernet(key)
    return f.encrypt(data)


def decrypt(data: bytes, password: str, salt: bytes):
    key = derive_key(password, salt)
    f = Fernet(key)
    return f.decrypt(data)
