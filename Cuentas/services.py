"""Service: reglas de negocio de autenticación. No conoce HTTP ni templates."""
from django.contrib.auth import authenticate, login, logout

from Cuentas.factories import UsuarioFactory


class AutenticacionService:
    def registrar(self, request, *, email, password, password2, nombre=""):
        usuario = UsuarioFactory.crear(email=email, password=password, nombre=nombre)
        login(request, usuario)
        return usuario

    def autenticar(self, request, *, email, password):
        usuario = authenticate(request, username=email, password=password)
        if usuario is None:
            raise ValueError("Correo o contraseña incorrectos.")
        login(request, usuario)
        return usuario

    def cerrar_sesion(self, request):
        logout(request)