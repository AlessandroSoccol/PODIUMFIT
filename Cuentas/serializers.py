"""
Serializers: unica capa autorizada para validar datos de entrada (formularios de
login/registro) y para dar forma a los datos de salida (usuario autenticado).
Las views NO deben validar ni transformar estos datos por su cuenta.
"""
from django.contrib.auth.models import User
from rest_framework import serializers

DOMINIO_PERMITIDO = "@eafit.edu.co"


def validar_correo_institucional(valor):
    if not valor.lower().endswith(DOMINIO_PERMITIDO):
        raise serializers.ValidationError(
            f"Debes usar un correo institucional que termine en {DOMINIO_PERMITIDO}."
        )


class RegistroSerializer(serializers.Serializer):
    """Valida los datos de entrada para crear una cuenta nueva."""

    nombre = serializers.CharField(max_length=150, required=False, allow_blank=True)
    email = serializers.EmailField(validators=[validar_correo_institucional])
    password = serializers.CharField(min_length=8, write_only=True)
    password2 = serializers.CharField(min_length=8, write_only=True)

    def validate_email(self, value):
        value = value.lower().strip()
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ya existe una cuenta registrada con ese correo.")
        return value

    def validate(self, datos):
        if datos["password"] != datos["password2"]:
            raise serializers.ValidationError({"password2": "Las contraseñas no coinciden."})
        return datos


class LoginSerializer(serializers.Serializer):
    """Valida los datos de entrada para iniciar sesión."""

    email = serializers.EmailField(validators=[validar_correo_institucional])
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        return value.lower().strip()


class UsuarioSerializer(serializers.ModelSerializer):
    """Da forma a los datos de salida del usuario autenticado."""

    email = serializers.CharField(source="username", read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "first_name"]
        read_only_fields = fields