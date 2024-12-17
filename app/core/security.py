from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from app.core.config import get_settings
from cryptography.fernet import Fernet
from base64 import b64encode, b64decode

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Verifica si una contraseña coincide con su hash
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Genera un hash seguro de la contraseña
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


#  Crea un token JWT para autenticación
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def get_encryption_key():
    # Usar una clave secreta desde las variables de entorno
    return settings.FINGERPRINT_ENCRYPTION_KEY


def encrypt_fingerprint(template: str) -> str:
    f = Fernet(get_encryption_key())
    encrypted = f.encrypt(template.encode())
    return b64encode(encrypted).decode()


def decrypt_fingerprint(encrypted_template: str) -> str:
    f = Fernet(get_encryption_key())
    decrypted = f.decrypt(b64decode(encrypted_template))
    return decrypted.decode()
