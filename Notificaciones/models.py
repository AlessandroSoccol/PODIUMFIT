from django.conf import settings
from django.db import models


class Notificacion(models.Model):
    TIPO_ESPACIO = "espacio"
    TIPO_INDUMENTARIA = "indumentaria"
    TIPO_CHOICES = [
        (TIPO_ESPACIO, "Espacio"),
        (TIPO_INDUMENTARIA, "Indumentaria"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notificaciones",
    )
    mensaje = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default=TIPO_ESPACIO)
    leida = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self):
        return f"[{self.usuario}] {self.mensaje}"