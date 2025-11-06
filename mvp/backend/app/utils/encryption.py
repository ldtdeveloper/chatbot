"""
Encryption utilities for API keys
"""
from cryptography.fernet import Fernet
from app.config import settings
import base64
import hashlib


def get_encryption_key() -> bytes:
    """Generate encryption key from secret key"""
    key = hashlib.sha256(settings.secret_key.encode()).digest()
    return base64.urlsafe_b64encode(key)


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key"""
    f = Fernet(get_encryption_key())
    return f.encrypt(api_key.encode()).decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key"""
    f = Fernet(get_encryption_key())
    return f.decrypt(encrypted_key.encode()).decode()

