import os


class Notificador:
    def enviar_confirmacion(self, destinatario, mensaje):
        raise NotImplementedError


class NotificadorConsola(Notificador):
    """Modo MOCK: no envía nada real, solo imprime en consola (útil en desarrollo/pruebas)."""

    def enviar_confirmacion(self, destinatario, mensaje):
        print(f"[MOCK] Para: {destinatario} | Mensaje: {mensaje}")


class NotificadorEmail(Notificador):
    """Modo REAL: envía un correo de verdad usando el backend de email de Django."""

    def enviar_confirmacion(self, destinatario, mensaje):
        from django.core.mail import send_mail
        send_mail(
            subject="Confirmación de reserva",
            message=mensaje,
            from_email=None,  # usa DEFAULT_FROM_EMAIL de settings.py
            recipient_list=[destinatario],
        )


class NotificadorFactory:
    @staticmethod
    def crear() -> Notificador:
        modo = os.environ.get("NOTIFICADOR_MODE", "MOCK")
        if modo == "REAL":
            return NotificadorEmail()
        return NotificadorConsola()