"""Password hashing and opaque sessions; no signed role claims or embedded credentials."""

import hashlib
import hmac
import secrets


def password_hash(password: str) -> str:
    """Versioned scrypt hash with independent 128-bit salt per account."""
    if len(password) < 16 or len(password) > 256:
        raise ValueError("Password must contain 16–256 characters")
    salt = secrets.token_bytes(16)
    key = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1, dklen=32)
    return f"scrypt1${salt.hex()}${key.hex()}"


def password_matches(password: str, encoded: str) -> bool:
    """Malformed hashes fail closed; password bytes are never logged."""
    if len(password) > 256:
        return False
    try:
        version, salt, expected = encoded.split("$")
        if version != "scrypt1":
            return False
        actual = hashlib.scrypt(
            password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1, dklen=32
        )
        return hmac.compare_digest(actual.hex(), expected)
    except (ValueError, TypeError):
        return False


def digest(value: str) -> str:
    """Session lookup stores only SHA-256 digests of random 256-bit tokens."""
    return hashlib.sha256(value.encode()).hexdigest()


def csrf_token(token: str) -> str:
    """A separate proof derived from the HttpOnly cookie, held only in client memory."""
    return hmac.new(token.encode(), b"nursery-csrf-v1", hashlib.sha256).hexdigest()
