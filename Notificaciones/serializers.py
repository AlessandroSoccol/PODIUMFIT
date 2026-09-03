"""Serializer de salida: da forma a las notificaciones que se muestran en la web."""
from rest_framework import serializers
from Notificaciones.models import Notificacion


class NotificacionSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)

    class Meta:
        model = Notificacion
        fields = ["id", "mensaje", "tipo", "tipo_display", "leida", "creado_en"]
        read_only_fields = fields