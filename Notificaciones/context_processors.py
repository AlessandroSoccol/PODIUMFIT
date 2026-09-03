"""Context processor: inyecta las notificaciones no leidas en cada template,
asi la pagina web las muestra sin que cada view tenga que pedirlas a mano."""
from Notificaciones.services import NotificacionService


def notificaciones_no_leidas(request):
    if not request.user.is_authenticated:
        return {"notificaciones_no_leidas": []}
    return {"notificaciones_no_leidas": NotificacionService().no_leidas(request.user)}