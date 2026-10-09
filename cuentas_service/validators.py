import re

from errors import ErrorDeValidacion

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validar_email(email, dominio_permitido, errores):
    if not email:
        errores.setdefault("email", []).append("Este campo es obligatorio.")
        return None
    email = email.lower().strip()
    if not _EMAIL_RE.match(email):
        errores.setdefault("email", []).append("Introduce un correo electrónico válido.")
    elif not email.endswith(dominio_permitido.lower()):
        errores.setdefault("email", []).append(
            f"Debes usar un correo institucional que termine en {dominio_permitido}."
        )
    return email


def validar_registro(data, dominio_permitido):
    errores = {}
    data = data or {}

    email = _validar_email(data.get("email"), dominio_permitido, errores)

    password = data.get("password") or ""
    password2 = data.get("password2") or ""
    if len(password) < 8:
        errores.setdefault("password", []).append(
            "Asegúrate de que este valor tenga al menos 8 caracteres."
        )
    if len(password2) < 8:
        errores.setdefault("password2", []).append(
            "Asegúrate de que este valor tenga al menos 8 caracteres."
        )
    if password and password2 and password != password2:
        errores.setdefault("password2", []).append("Las contraseñas no coinciden.")

    nombre = (data.get("nombre") or "").strip()
    if len(nombre) > 150:
        errores.setdefault("nombre", []).append("Máximo 150 caracteres.")

    if errores:
        raise ErrorDeValidacion(errores=errores)

    return {"email": email, "password": password, "nombre": nombre}


def validar_login(data, dominio_permitido):
    errores = {}
    data = data or {}

    email = _validar_email(data.get("email"), dominio_permitido, errores)

    password = data.get("password") or ""
    if not password:
        errores.setdefault("password", []).append("Este campo es obligatorio.")

    if errores:
        raise ErrorDeValidacion(errores=errores)

    return {"email": email, "password": password}
