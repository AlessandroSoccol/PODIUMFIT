"""
Views: SOLO orquestan. Reciben la petición, la pasan a un serializer para
validarla, delegan la logica de negocio al Service y renderizan el resultado.
Ninguna regla de negocio (validaciones de dominio, creacion de usuario, etc.)
vive aqui.
"""
from django.shortcuts import render, redirect
from django.views import View

from Cuentas.serializers import RegistroSerializer, LoginSerializer
from Cuentas.services import AutenticacionService


class RegistroView(View):
    template_name = "Cuentas/registro.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        serializer = RegistroSerializer(data=request.POST)
        if not serializer.is_valid():
            return render(request, self.template_name, {"errores": serializer.errors})

        AutenticacionService().registrar(request, **serializer.validated_data)
        return redirect("index")


class LoginView(View):
    template_name = "Cuentas/login.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        serializer = LoginSerializer(data=request.POST)
        if not serializer.is_valid():
            return render(request, self.template_name, {"errores": serializer.errors})

        try:
            AutenticacionService().autenticar(request, **serializer.validated_data)
        except ValueError as error:
            return render(request, self.template_name, {"error": str(error)})
        return redirect("index")


class LogoutView(View):
    def post(self, request):
        AutenticacionService().cerrar_sesion(request)
        return redirect("login")