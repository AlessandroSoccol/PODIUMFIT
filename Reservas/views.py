"""
Views: SOLO orquestan HTTP <-> Service. Un serializer valida/da forma a
los datos de entrada, el Factory ensambla el Service correcto, y el
Service ejecuta la logica de negocio. Ninguna regla de negocio (limites de
cantidad, bloqueo de espacios, calculo de vencimiento, etc.) vive aqui.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView

from Reservas.factories import ReservaEspacioServiceFactory, ReservaIndumentariaServiceFactory
from Reservas.models import Espacio, Indumentaria, ReservaEspacio, ReservaIndumentaria
from Reservas.serializers import (
    EspacioSerializer,
    IndumentariaSerializer,
    ReservaEspacioInputSerializer,
    ReservaEspacioOutputSerializer,
    ReservaIndumentariaInputSerializer,
    ReservaIndumentariaOutputSerializer,
)
from Reservas.services import ReservaEspacioService, ReservaIndumentariaService


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "Reservas/base.html"


class ReservarEspacioView(LoginRequiredMixin, View):
    template_name = "Reservas/reservar_espacio.html"

    def _contexto(self, extra=None):
        ReservaEspacioService.liberar_vencidas()
        espacios = Espacio.objects.all()
        reservas_activas = ReservaEspacio.objects.filter(activa=True).select_related("espacio")
        espacio_bloqueante = ReservaEspacioService.espacio_que_bloquea()
        contexto = {
            "espacios": EspacioSerializer(espacios, many=True).data,
            "reservas_activas": ReservaEspacioOutputSerializer(reservas_activas, many=True).data,
            "bloqueo_activo": espacio_bloqueante is not None,
            "espacio_bloqueante_id": espacio_bloqueante.id if espacio_bloqueante else None,
        }
        contexto.update(extra or {})
        return contexto

    def get(self, request):
        return render(request, self.template_name, self._contexto())

    def post(self, request):
        serializer = ReservaEspacioInputSerializer(data=request.POST)
        if not serializer.is_valid():
            return render(request, self.template_name, self._contexto({"errores": serializer.errors}))

        try:
            ReservaEspacioServiceFactory.crear().crear_reserva(
                usuario=request.user, **serializer.validated_data
            )
        except ValueError as error:
            return render(request, self.template_name, self._contexto({"error": str(error)}))
        return redirect("reservar_espacio")


class LiberarEspacioView(LoginRequiredMixin, View):
    def post(self, request, reserva_id):
        ReservaEspacioServiceFactory.crear().liberar_reserva(
            usuario=request.user, reserva_id=reserva_id
        )
        return redirect("reservar_espacio")


class ReservarIndumentariaView(LoginRequiredMixin, View):
    template_name = "Reservas/reservar_indumentaria.html"

    def _contexto(self, extra=None):
        ReservaIndumentariaService.devolver_vencidas()
        items = Indumentaria.objects.all()
        reservas_activas = ReservaIndumentaria.objects.filter(activa=True).select_related("indumentaria")
        contexto = {
            "items": IndumentariaSerializer(items, many=True).data,
            "reservas_activas": ReservaIndumentariaOutputSerializer(reservas_activas, many=True).data,
        }
        contexto.update(extra or {})
        return contexto

    def get(self, request):
        return render(request, self.template_name, self._contexto())

    def post(self, request):
        serializer = ReservaIndumentariaInputSerializer(data=request.POST)
        if not serializer.is_valid():
            return render(request, self.template_name, self._contexto({"errores": serializer.errors}))

        try:
            ReservaIndumentariaServiceFactory.crear().crear_reserva(
                usuario=request.user, **serializer.validated_data
            )
        except ValueError as error:
            return render(request, self.template_name, self._contexto({"error": str(error)}))
        return redirect("reservar_indumentaria")


class DevolverIndumentariaView(LoginRequiredMixin, View):
    def post(self, request, reserva_id):
        ReservaIndumentariaServiceFactory.crear().devolver_reserva(
            usuario=request.user, reserva_id=reserva_id
        )
        return redirect("reservar_indumentaria")