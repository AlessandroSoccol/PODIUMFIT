# Reservas/domain/builders.py
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
        if self._duracion_horas < 1 or self._duracion_horas > 2:
            raise ValueError("La duración máxima de una reserva es de 2 horas.")

    def build(self):
        self._validar()
        self._espacio.cantidad_disponible -= 1
        self._espacio.save()
        return ReservaEspacio.objects.create(
            espacio=self._espacio,
            hora_inicio=self._hora_inicio,
            duracion_horas=self._duracion_horas,
        )


class ReservaIndumentariaBuilder:
    """Construye una ReservaIndumentaria paso a paso, validando stock antes de guardar."""

    def __init__(self):
        self._indumentaria = None
        self._hora_inicio = None
        self._duracion_horas = 1

    def de_indumentaria(self, indumentaria):
        self._indumentaria = indumentaria
        return self

    def a_las(self, hora_inicio):
        self._hora_inicio = hora_inicio
        return self

    def con_duracion(self, horas):
        self._duracion_horas = horas
        return self

    def _validar(self):
        if self._indumentaria is None:
            raise ValueError("Debes seleccionar una prenda.")
        if self._indumentaria.stock < 1:
            raise ValueError("No queda stock de esta prenda.")
        if not self._hora_inicio:
            raise ValueError("Debes seleccionar una hora de inicio.")
        if self._duracion_horas < 1 or self._duracion_horas > 2:
            raise ValueError("La duración máxima de una reserva es de 2 horas.")

    def build(self):
        self._validar()
        self._indumentaria.stock -= 1
        self._indumentaria.save()
        return ReservaIndumentaria.objects.create(
            indumentaria=self._indumentaria,
            hora_inicio=self._hora_inicio,
            duracion_horas=self._duracion_horas,
        )