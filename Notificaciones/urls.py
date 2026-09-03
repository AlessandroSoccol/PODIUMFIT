from django.urls import path
from Notificaciones.views import NotificacionesNoLeidasView, MarcarNotificacionLeidaView

urlpatterns = [
    path("no-leidas/", NotificacionesNoLeidasView.as_view(), name="notificaciones_no_leidas"),
    path("<int:notificacion_id>/leida/", MarcarNotificacionLeidaView.as_view(), name="notificacion_marcar_leida"),
]