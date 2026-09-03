"""
Factory: ensambla los Services de Reservas con sus dependencias (el
Notificador que provee la app Notificaciones), para que las views no
necesiten saber como se construyen ni de donde vienen esas dependencias.
"""
from Notificaciones.factories import NotificadorFactory


class ReservaEspacioServiceFactory:
    @staticmethod
    def crear():
        from Reservas.services import ReservaEspacioService

        return ReservaEspacioService(notificador=NotificadorFactory.crear())


class ReservaIndumentariaServiceFactory:
    @staticmethod
    def crear():
        from Reservas.services import ReservaIndumentariaService

        return ReservaIndumentariaService(notificador=NotificadorFactory.crear())