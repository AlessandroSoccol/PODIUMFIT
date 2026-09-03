from datetime import timedelta

from django.utils import timezone

from Reservas.domain import reglas
from Reservas.models import ReservaEspacio, ReservaIndumentaria


class ReservaEspacioBuilder:
    """Construye una ReservaEspacio paso a paso, validando antes de guardar."""

    def __init__(self):
        self._espacio = None
        self._hora_inicio = None
        self._duracion_horas = 1

    def en_espacio(self, espacio):
        self._espacio = espacio
        return self

    def a_las(self, hora_inicio):
        self._hora_inicio = hora_inicio
        return self

    def con_duracion(self, horas):
        self._duracion_horas = horas
        return self

    def _validar(self):
        if self._espacio is None:
            raise ValueError("Debes seleccionar un espacio.")
        if self._espacio.cantidad_disponible < 1:
            raise ValueError("No quedan unidades disponibles de este espacio.")
        if not self._hora_inicio:
            raise ValueError("Debes seleccionar una hora de inicio.")
        if self._duracion_horas < 1 or self._duracion_horas > reglas.DURACION_MAXIMA_ESPACIO_HORAS:
            raise ValueError(
                f"La duración máxima de una reserva de espacio es de {reglas.DURACION_MAXIMA_ESPACIO_HORAS} hora."
            )
        # Mientras haya un espacio distinto activo y vigente, los demás quedan bloqueados.
        reglas.validar_disponibilidad_global_espacio(self._espacio)

    def build(self):
        self._validar()
        self._espacio.cantidad_disponible -= 1
        self._espacio.save()
        fin = timezone.now() + timedelta(hours=self._duracion_horas)
        return ReservaEspacio.objects.create(
            espacio=self._espacio,
            hora_inicio=self._hora_inicio,
            duracion_horas=self._duracion_horas,
            fin=fin,
        )


class ReservaIndumentariaBuilder:
    """Construye una ReservaIndumentaria paso a paso, validando stock y las
    unidades máximas por tipo de instrumental antes de guardar."""

    def __init__(self):
        self._indumentaria = None
        self._hora_inicio = None
        self._duracion_horas = 1
        self._cantidad = 1

    def de_indumentaria(self, indumentaria):
        self._indumentaria = indumentaria
        return self

    def a_las(self, hora_inicio):
        self._hora_inicio = hora_inicio
        return self

    def con_duracion(self, horas):
        self._duracion_horas = horas
        return self

    def con_cantidad(self, cantidad):
        self._cantidad = cantidad
        return self

    def _validar(self):
        if self._indumentaria is None:
            raise ValueError("Debes seleccionar una prenda.")
        if not self._hora_inicio:
            raise ValueError("Debes seleccionar una hora de inicio.")
        if self._duracion_horas < 1 or self._duracion_horas > reglas.DURACION_MAXIMA_INDUMENTARIA_HORAS:
            raise ValueError(
                f"La duración máxima de una reserva es de {reglas.DURACION_MAXIMA_INDUMENTARIA_HORAS} horas."
            )
        reglas.validar_cantidad_indumentaria(self._indumentaria, self._cantidad)

    def build(self):
        self._validar()
        self._indumentaria.stock -= self._cantidad
        self._indumentaria.save()
        fin = timezone.now() + timedelta(hours=self._duracion_horas)
        return ReservaIndumentaria.objects.create(
            indumentaria=self._indumentaria,
            hora_inicio=self._hora_inicio,
            duracion_horas=self._duracion_horas,
            cantidad=self._cantidad,
            fin=fin,
        )