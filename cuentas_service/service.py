from datetime import datetime, timedelta, timezone

import jwt

from errors import ConflictoDeRecurso, CredencialesInvalidas
from security import hacer_hash, verificar_password


class AutenticacionService:
    def __init__(self, repo, config):
        self.repo = repo
        self.config = config

    def _crear_usuario(self, *, email, password, nombre=""):
        password_hash = hacer_hash(password, self.config.PBKDF2_ITERATIONS)
        user_id = self.repo.crear(
            username=email,
            email=email,
            first_name=nombre,
            password_hash=password_hash,
        )
        return {"id": user_id, "email": email, "first_name": nombre}

    def registrar(self, *, email, password, nombre=""):
        if self.repo.existe_username(email):
            raise ConflictoDeRecurso(
                "Ya existe una cuenta registrada con ese correo.", campo="email"
            )
        usuario = self._crear_usuario(email=email, password=password, nombre=nombre)
        token = self._emitir_token(usuario["id"], usuario["email"])
        return {"usuario": usuario, "token": token}

    def autenticar(self, *, email, password):
        fila = self.repo.obtener_por_username(email)
        if fila is None or not verificar_password(password, fila["password"]):
            raise CredencialesInvalidas("Correo o contraseña incorrectos.")
        if not fila["is_active"]:
            raise CredencialesInvalidas("La cuenta está inactiva.")
        self.repo.actualizar_last_login(fila["id"])
        usuario = {
            "id": fila["id"],
            "email": fila["username"],
            "first_name": fila["first_name"],
        }
        token = self._emitir_token(fila["id"], fila["username"])
        return {"usuario": usuario, "token": token}

    def perfil_desde_token(self, token):
        payload = self._decodificar_token(token)
        fila = self.repo.obtener_por_username(payload["email"])
        if fila is None:
            raise CredencialesInvalidas("Token válido pero el usuario ya no existe.")
        return {
            "id": fila["id"],
            "email": fila["username"],
            "first_name": fila["first_name"],
        }

    def _emitir_token(self, user_id, email):
        ahora = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "email": email,
            "iat": ahora,
            "exp": ahora + timedelta(minutes=self.config.JWT_EXPIRES_MIN),
        }
        return jwt.encode(payload, self.config.SECRET_KEY, algorithm="HS256")

    def _decodificar_token(self, token):
        try:
            return jwt.decode(token, self.config.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise CredencialesInvalidas("El token ha expirado.")
        except jwt.InvalidTokenError:
            raise CredencialesInvalidas("Token inválido.")
