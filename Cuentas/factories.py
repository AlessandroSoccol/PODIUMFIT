"""Factory: unico punto responsable de construir instancias de User."""
from django.contrib.auth.models import User


class UsuarioFactory:
    """Encapsula la creación de usuarios a partir de datos ya validados
    (por RegistroSerializer). El username se hace igual al correo para poder
    autenticar con el backend estándar de Django."""

    @staticmethod
    def crear(email, password, nombre=""):
        return User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=nombre,
        )