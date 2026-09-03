"""
Serializers: unica capa autorizada para validar los datos que llegan por
POST y para dar forma a los datos que se muestran (contexto de template /
JSON). Las views nunca leen ni interpretan request.POST directamente.
"""
from rest_framework import serializers

from Reservas.domain import reglas
from Reservas.models import Espacio, Indumentaria, ReservaEspacio, ReservaIndumentaria


class EspacioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Espacio
        fields = ["id", "nombre", "cantidad_disponible"]
        read_only_fields = fields


class IndumentariaSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    limite_por_reserva = serializers.SerializerMethodField()

    class Meta:
        model = Indumentaria
        fields = ["id", "nombre", "talla", "tipo", "tipo_display", "stock", "limite_por_reserva"]
        read_only_fields = fields

    def get_limite_por_reserva(self, obj):
        return reglas.limite_cantidad_para_tipo(obj.tipo)


class ReservaEspacioOutputSerializer(serializers.ModelSerializer):
    espacio = EspacioSerializer(read_only=True)

    class Meta:
        model = ReservaEspacio
        fields = ["id", "espacio", "hora_inicio", "duracion_horas", "fin", "activa"]
        read_only_fields = fields


class ReservaIndumentariaOutputSerializer(serializers.ModelSerializer):
    indumentaria = IndumentariaSerializer(read_only=True)

    class Meta:
        model = ReservaIndumentaria
        fields = ["id", "indumentaria", "hora_inicio", "duracion_horas", "cantidad", "fin", "activa"]
        read_only_fields = fields


class ReservaEspacioInputSerializer(serializers.Serializer):
    espacio_id = serializers.IntegerField()
    hora_inicio = serializers.CharField(max_length=8)
    duracion_horas = serializers.IntegerField(
        default=1, min_value=1, max_value=reglas.DURACION_MAXIMA_ESPACIO_HORAS
    )

    def validate_espacio_id(self, value):
        if not Espacio.objects.filter(pk=value).exists():
            raise serializers.ValidationError("El espacio indicado no existe.")
        return value


class ReservaIndumentariaInputSerializer(serializers.Serializer):
    indumentaria_id = serializers.IntegerField()
    hora_inicio = serializers.CharField(max_length=8)
    duracion_horas = serializers.IntegerField(
        default=1, min_value=1, max_value=reglas.DURACION_MAXIMA_INDUMENTARIA_HORAS
    )
    cantidad = serializers.IntegerField(default=1, min_value=1)

    def validate_indumentaria_id(self, value):
        if not Indumentaria.objects.filter(pk=value).exists():
            raise serializers.ValidationError("La indumentaria indicada no existe.")
        return value