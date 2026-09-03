"""Service: reglas de negocio de notificaciones (crear, listar, marcar como leidas)."""
from Notificaciones.models import Notificacion


class NotificacionService:
    def crear(self, usuario, mensaje, tipo=Notificacion.TIPO_ESPACIO):
        return Notificacion.objects.create(usuario=usuario, mensaje=mensaje, tipo=tipo)

    def no_leidas(self, usuario):
        return Notificacion.objects.filter(usuario=usuario, leida=False)

    def marcar_leida(self, usuario, notificacion_id):
        actualizadas = Notificacion.objects.filter(
            pk=notificacion_id, usuario=usuario
        ).update(leida=True)
        if not actualizadas:
            raise ValueError("La notificación no existe o no te pertenece.")

    def marcar_todas_leidas(self, usuario):
        self.no_leidas(usuario).update(leida=True)