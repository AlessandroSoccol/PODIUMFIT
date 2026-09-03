"""Views delgadas: reciben la peticion, delegan al Service y serializan la salida."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

from Notificaciones.serializers import NotificacionSerializer
from Notificaciones.services import NotificacionService


class NotificacionesNoLeidasView(LoginRequiredMixin, View):
    """Devuelve (JSON) las notificaciones no leidas del usuario autenticado,
    para mostrarlas en la campanita de la página."""

    def get(self, request):
        notificaciones = NotificacionService().no_leidas(request.user)
        datos = NotificacionSerializer(notificaciones, many=True).data
        return JsonResponse({"notificaciones": datos})


class MarcarNotificacionLeidaView(LoginRequiredMixin, View):
    def post(self, request, notificacion_id):
        try:
            NotificacionService().marcar_leida(request.user, notificacion_id)
        except ValueError as error:
            return JsonResponse({"error": str(error)}, status=404)
        return JsonResponse({"ok": True})