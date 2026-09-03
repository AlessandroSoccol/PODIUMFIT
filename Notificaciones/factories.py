"""
Factory: decide, segun configuracion, que estrategia(s) de envio de
notificaciones se usan (Strategy pattern) y ensambla el objeto final que
consumen otras apps (p. ej. Reservas). Siempre incluye la notificacion web
para que la reserva se refleje en la propia pagina.
"""
import os
from abc import ABC, abstractmethod

from Notificaciones.models import Notificacion
from Notificaciones.services import NotificacionService


class Notificador(ABC):
    @abstractmethod
    def enviar_confirmacion(self, usuario, mensaje, tipo=Notificacion.TIPO_ESPACIO):
        raise NotImplementedError


class NotificadorConsola(Notificador):
    """Modo desarrollo/pruebas: solo imprime en consola."""

    def enviar_confirmacion(self, usuario, mensaje, tipo=Notificacion.TIPO_ESPACIO):
        print(f"[MOCK] Para: {usuario} | Mensaje: {mensaje}")


class NotificadorEmail(Notificador):
    """Modo real: envía un correo usando el backend de email de Django."""

    def enviar_confirmacion(self, usuario, mensaje, tipo=Notificacion.TIPO_ESPACIO):
        from django.core.mail import send_mail

        destinatario = getattr(usuario, "email", None)
        if not destinatario:
            return
        send_mail(
            subject="Confirmación de reserva - PodiumFit",
            message=mensaje,
            from_email=None,
            recipient_list=[destinatario],
        )


class NotificadorWeb(Notificador):
    """Persiste la notificación para que se muestre dentro de la página web."""

    def __init__(self, service=None):
        self.service = service or NotificacionService()

    def enviar_confirmacion(self, usuario, mensaje, tipo=Notificacion.TIPO_ESPACIO):
        if usuario is None or not getattr(usuario, "is_authenticated", False):
            return
        self.service.crear(usuario=usuario, mensaje=mensaje, tipo=tipo)


class NotificadorCompuesto(Notificador):
    """Envía por varias estrategias a la vez (p. ej. web + email)."""

    def __init__(self, estrategias):
        self.estrategias = estrategias

    def enviar_confirmacion(self, usuario, mensaje, tipo=Notificacion.TIPO_ESPACIO):
        for estrategia in self.estrategias:
            estrategia.enviar_confirmacion(usuario, mensaje, tipo)


class NotificadorFactory:
    @staticmethod
    def crear() -> Notificador:
        modo = os.environ.get("NOTIFICADOR_MODE", "MOCK")
        estrategia_externa = NotificadorEmail() if modo == "REAL" else NotificadorConsola()
        # La notificación web siempre se incluye para que la reserva se vea en la página.
        return NotificadorCompuesto([estrategia_externa, NotificadorWeb()])