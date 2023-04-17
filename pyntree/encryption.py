try:
    from cryptography.fernet import Fernet
    from argon2.low_level import hash_secret_raw, Type
    import base64
    SUPPORTED = True
except:
    SUPPORTED = False
    from pyntree.errors import Error


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


def check():  # Determine whether the necessary packages are installed
    if not SUPPORTED:
        raise Error.EncryptionNotAvailable(
            'Your system is missing the packages needed to support encryption. Please run \
            "pip install pyntree[encryption]" to install these non-standard packages.'
        )