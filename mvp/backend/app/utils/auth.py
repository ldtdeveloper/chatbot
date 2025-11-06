"""
Authentication utilities
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import hashlib
from app.config import settings

# Lazy initialization of passlib to avoid startup errors
_pwd_context = None

def _get_pwd_context():
    """Get passlib context, initializing it lazily"""
    global _pwd_context
    if _pwd_context is None:
        try:
            from passlib.context import CryptContext
            _pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        except Exception:
            # If passlib fails to initialize, we'll just use direct bcrypt
            _pwd_context = None
    return _pwd_context


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash
    
    Supports two formats:
    1. New format: bcrypt(SHA256(password)) - for passwords of any length
    2. Old format: bcrypt(password) - for backward compatibility
    """
    import bcrypt
    
    # Hash password with SHA256 first (for new password format)
    password_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
    
    # Try new format first: bcrypt(SHA256(password))
    try:
        if bcrypt.checkpw(password_hash.encode('utf-8'), hashed_password.encode('utf-8')):
            return True
    except:
        pass
    
    # Try old format for backward compatibility: bcrypt(password)
    # Only if password is <= 72 bytes (bcrypt limit)
    try:
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) <= 72:
            if bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8')):
                return True
    except:
        pass
    
    # Fallback: try with passlib (for old passwords created with passlib)
    # Only if password is <= 72 bytes
    try:
        pwd_context = _get_pwd_context()
        if pwd_context is not None:
            password_bytes = plain_password.encode('utf-8')
            if len(password_bytes) <= 72:
                return pwd_context.verify(plain_password, hashed_password)
    except:
        pass
    
    return False


def get_password_hash(password: str) -> str:
    """Hash a password
    
    Since bcrypt has a 72-byte limit, we first hash the password with SHA256
    (which produces a fixed 64-byte hex string), then bcrypt that.
    This allows us to handle passwords of any length while maintaining security.
    """
    import bcrypt
    # Hash with SHA256 first to ensure it's always under 72 bytes
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    # Now bcrypt the SHA256 hash (which is always 64 bytes) using direct bcrypt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_hash.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    # Convert sub to string if it's an integer (JWT spec requires string)
    if "sub" in to_encode and isinstance(to_encode["sub"], int):
        to_encode["sub"] = str(to_encode["sub"])
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None
    except Exception:
        return None

