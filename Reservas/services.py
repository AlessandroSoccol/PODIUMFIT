"""
Service: orquesta el caso de uso (obtener las entidades, invocar al Builder
de dominio, notificar el resultado). No parsea HTTP ni conoce templates:
recibe datos ya validados por un serializer.
"""
from django.shortcuts import get_object_or_404
from django.utils import timezone

from Reservas.domain import reglas
from Reservas.domain.builders import ReservaEspacioBuilder, ReservaIndumentariaBuilder
from Reservas.models import Espacio, Indumentaria, ReservaEspacio, ReservaIndumentaria


class ReservaEspacioService:
    def __init__(self, notificador):
        self.notificador = notificador

    def crear_reserva(self, usuario, espacio_id, hora_inicio, duracion_horas=1):
        espacio = get_object_or_404(Espacio, pk=espacio_id)
        reserva = (
            ReservaEspacioBuilder()
            .en_espacio(espacio)
            .a_las(hora_inicio)
            .con_duracion(duracion_horas)
            .build()
        )
        self.notificador.enviar_confirmacion(
            usuario=usuario,
            mensaje=(
                f"Reserva de espacio confirmada: {espacio.nombre} a las {hora_inicio}. "
                f"Vence a las {reserva.fin.strftime('%H:%M')}."
            ),
            tipo="espacio",
        )
        return reserva

    def liberar_reserva(self, usuario, reserva_id):
        reserva = get_object_or_404(ReservaEspacio, pk=reserva_id, activa=True)
        reserva.activa = False
        reserva.save()
        reserva.espacio.cantidad_disponible += 1
        reserva.espacio.save()
        self.notificador.enviar_confirmacion(
            usuario=usuario,
            mensaje=f"Espacio liberado: {reserva.espacio.nombre}. Ya está disponible de nuevo.",
            tipo="espacio",
        )

    @staticmethod
    def bloqueo_activo():
        return reglas.hay_bloqueo_de_espacios()

    @staticmethod
    def espacio_que_bloquea():
        return reglas.espacio_que_bloquea()

    @staticmethod
    def liberar_vencidas():
        """El tiempo de cada reserva se va descontando; cuando llega a cero
        (fin <= ahora) el espacio se libera automáticamente sin esperar a
        que el usuario presione 'Ya liberé este espacio'."""
        vencidas = ReservaEspacio.objects.filter(
            activa=True, fin__lte=timezone.now()
        ).select_related("espacio")
        for reserva in vencidas:
            reserva.activa = False
            reserva.save(update_fields=["activa"])
            reserva.espacio.cantidad_disponible += 1
            reserva.espacio.save(update_fields=["cantidad_disponible"])


class ReservaIndumentariaService:
    def __init__(self, notificador):
        self.notificador = notificador

    def crear_reserva(self, usuario, indumentaria_id, hora_inicio, duracion_horas=1, cantidad=1):
        indumentaria = get_object_or_404(Indumentaria, pk=indumentaria_id)
        reserva = (
            ReservaIndumentariaBuilder()
            .de_indumentaria(indumentaria)
            .a_las(hora_inicio)
            .con_duracion(duracion_horas)
            .con_cantidad(cantidad)
            .build()
        )
        self.notificador.enviar_confirmacion(
            usuario=usuario,
            mensaje=f"Reserva confirmada: {cantidad}x {indumentaria.nombre} a las {hora_inicio}.",
            tipo="indumentaria",
        )
        return reserva

    def devolver_reserva(self, usuario, reserva_id):
        reserva = get_object_or_404(ReservaIndumentaria, pk=reserva_id, activa=True)
        reserva.activa = False
        reserva.save()
        reserva.indumentaria.stock += reserva.cantidad
        reserva.indumentaria.save()
        self.notificador.enviar_confirmacion(
            usuario=usuario,
            mensaje=f"Devolviste {reserva.cantidad}x {reserva.indumentaria.nombre}. ¡Gracias!",
            tipo="indumentaria",
        )

    @staticmethod
    def devolver_vencidas():
        """El tiempo de cada préstamo se va descontando; cuando llega a cero
        (fin <= ahora) la indumentaria se devuelve automáticamente al stock."""
        vencidas = ReservaIndumentaria.objects.filter(
            activa=True, fin__lte=timezone.now()
        ).select_related("indumentaria")
        for reserva in vencidas:
            reserva.activa = False
            reserva.save(update_fields=["activa"])
            reserva.indumentaria.stock += reserva.cantidad
            reserva.indumentaria.save(update_fields=["stock"])