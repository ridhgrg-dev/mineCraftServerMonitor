import unicodedata
from hashlib import sha256
from secrets import token_urlsafe

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

_password_hasher = PasswordHasher()


def new_session_token() -> str:
    return token_urlsafe(32)


def hash_session_token(token: str) -> bytes:
    return sha256(token.encode("utf-8")).digest()


def normalize_email(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).strip().lower()
    if not normalized or len(normalized) > 320 or "@" not in normalized:
        raise ValueError("A valid email address is required")
    return normalized


def hash_password(password: str) -> str:
    if not 12 <= len(password) <= 1024:
        raise ValueError("Password length is invalid")
    return _password_hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _password_hasher.verify(password_hash, password)
    except InvalidHashError, VerifyMismatchError:
        return False
