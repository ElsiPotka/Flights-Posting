import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.schemas.auth_token import TokenData

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def read_key_file(path: str) -> str:
    """Read the auth keys"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError as exc:
        raise RuntimeError(f"Key file not found: {path}") from exc
    except Exception as e:
        raise RuntimeError(f"Error reading key file: {e}") from e


PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH")
PUBLIC_KEY_PATH = os.getenv("PUBLIC_KEY_PATH")
ALGORITHM = os.getenv("ALGORITHM", "RS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "10080"))

if PRIVATE_KEY_PATH is None:
    raise RuntimeError("PRIVATE_KEY_PATH environment variable is not set")
if PUBLIC_KEY_PATH is None:
    raise RuntimeError("PUBLIC_KEY_PATH environment variable is not set")

SECRET_KEY = read_key_file(PRIVATE_KEY_PATH)
PUBLIC_KEY = read_key_file(PUBLIC_KEY_PATH)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create the access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    """Create the refresh token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    """Verifies token"""
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return TokenData(email=email)
    except JWTError as exc:
        raise credentials_exception from exc
