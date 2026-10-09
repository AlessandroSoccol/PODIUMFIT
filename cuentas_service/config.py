import os


class Config:
    SECRET_KEY = os.environ.get("CUENTAS_SECRET_KEY", "cambia-esta-clave-en-produccion")

    JWT_EXPIRES_MIN = int(os.environ.get("CUENTAS_JWT_EXPIRES_MIN", "60"))

    DB_PATH = os.environ.get("CUENTAS_DB_PATH", "/data/db.sqlite3")

    DOMINIO_PERMITIDO = os.environ.get("CUENTAS_DOMINIO", "@eafit.edu.co")

    PBKDF2_ITERATIONS = int(os.environ.get("CUENTAS_PBKDF2_ITERATIONS", "1500000"))
