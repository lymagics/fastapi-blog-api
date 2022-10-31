import hashlib
import secrets


def generate_password_hash(password: str, algorithm = hashlib.md5) -> str:
    """Create password hash from raw string."""
    salt = secrets.token_urlsafe(5)
    hash = algorithm(f"{password}{salt}".encode("utf-8")).hexdigest()
    return f"{salt}${hash}" 


def check_password_hash(password_hash: str, password: str, algorithm = hashlib.md5) -> bool:
    """Check is password is valid."""
    salt, hash = password_hash.split("$")
    return hash == algorithm(f"{password}{salt}".encode("utf-8")).hexdigest()
