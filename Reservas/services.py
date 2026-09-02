# Reservas/services.py
from Reservas.domain.builders import ReservaEspacioBuilder, ReservaIndumentariaBuilder
from Reservas.infra.factories import NotificadorFactory


class ReservaEspacioService:
    def __init__(self, notificador=None):
        self.notificador = notificador or NotificadorFactory.crear()

    def crear_reserva(self, espacio, hora_inicio, duracion_horas):
        reserva = (
            ReservaEspacioBuilder()
            .en_espacio(espacio)
            .a_las(hora_inicio)
            .con_duracion(duracion_horas)
            .build()
        )
        self.notificador.enviar_confirmacion(
            destinatario="log",
            mensaje=f"Reserva de espacio: {espacio.nombre} a las {hora_inicio}. Quedan {espacio.cantidad_disponible}."
        )
        return reserva

    def liberar_reserva(self, reserva):
        if not reserva.activa:
            raise ValueError("Esta reserva ya fue liberada.")
        reserva.activa = False
        reserva.save()
        reserva.espacio.cantidad_disponible += 1
        reserva.espacio.save()
        self.notificador.enviar_confirmacion(
            destinatario="log",
            mensaje=f"Espacio liberado: {reserva.espacio.nombre}. Ahora disponibles: {reserva.espacio.cantidad_disponible}."
        )


class ReservaIndumentariaService:
    def __init__(self, notificador=None):
        self.notificador = notificador or NotificadorFactory.crear()

    def crear_reserva(self, indumentaria, hora_inicio, duracion_horas):
        reserva = (
            ReservaIndumentariaBuilder()
            .de_indumentaria(indumentaria)
            .a_las(hora_inicio)
            .con_duracion(duracion_horas)
            .build()
        )
        self.notificador.enviar_confirmacion(
            destinatario="log",
            mensaje=f"Reserva de indumentaria: {indumentaria.nombre} a las {hora_inicio}. Quedan {indumentaria.stock}."
        )
        return reserva

    def devolver_reserva(self, reserva):
        if not reserva.activa:
            raise ValueError("Esta reserva ya fue devuelta.")
        reserva.activa = False
        reserva.save()
        reserva.indumentaria.stock += 1
        reserva.indumentaria.save()
        self.notificador.enviar_confirmacion(
            destinatario="log",
            mensaje=f"Indumentaria devuelta: {reserva.indumentaria.nombre}. Ahora disponibles: {reserva.indumentaria.stock}."
        )