import base64
import hashlib
import hmac
import secrets

ALGORITHM = "pbkdf2_sha256"


def hacer_hash(password: str, iterations: int, salt: str | None = None) -> str:
    if salt is None:
        salt = secrets.token_hex(6)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations)
    hash_b64 = base64.b64encode(dk).decode("ascii").strip()
    return f"{ALGORITHM}${iterations}${salt}${hash_b64}"


def verificar_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt, _ = encoded.split("$", 3)
    except ValueError:
        return False
    if algorithm != ALGORITHM:
        return False
    try:
        iterations = int(iterations)
    except ValueError:
        return False
    recomputado = hacer_hash(password, iterations, salt)
    return hmac.compare_digest(recomputado, encoded)
