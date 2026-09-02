# Reservas/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView

from Reservas.models import Espacio, Indumentaria, ReservaEspacio, ReservaIndumentaria
from Reservas.services import ReservaEspacioService, ReservaIndumentariaService


class IndexView(TemplateView):
    template_name = "Reservas/base.html"


class ReservarEspacioView(View):
    def get(self, request):
        espacios = Espacio.objects.all()
        reservas_activas = ReservaEspacio.objects.filter(activa=True).select_related("espacio")
        return render(request, "Reservas/reservar_espacio.html", {
            "espacios": espacios,
            "reservas_activas": reservas_activas,
        })

    def post(self, request):
        espacio = get_object_or_404(Espacio, pk=request.POST.get("espacio_id"))
        hora_inicio = request.POST.get("hora_inicio")
        duracion = int(request.POST.get("duracion_horas", 1))
        try:
            ReservaEspacioService().crear_reserva(espacio, hora_inicio, duracion)
        except ValueError as e:
            espacios = Espacio.objects.all()
            reservas_activas = ReservaEspacio.objects.filter(activa=True).select_related("espacio")
            return render(request, "Reservas/reservar_espacio.html", {
                "espacios": espacios, "reservas_activas": reservas_activas, "error": str(e),
            })
        return redirect("reservar_espacio")


class LiberarEspacioView(View):
    def post(self, request, reserva_id):
        reserva = get_object_or_404(ReservaEspacio, pk=reserva_id, activa=True)
        ReservaEspacioService().liberar_reserva(reserva)
        return redirect("reservar_espacio")


class ReservarIndumentariaView(View):
    def get(self, request):
        items = Indumentaria.objects.all()
        reservas_activas = ReservaIndumentaria.objects.filter(activa=True).select_related("indumentaria")
        return render(request, "Reservas/reservar_indumentaria.html", {
            "items": items,
            "reservas_activas": reservas_activas,
        })

    def post(self, request):
        indumentaria = get_object_or_404(Indumentaria, pk=request.POST.get("indumentaria_id"))
        hora_inicio = request.POST.get("hora_inicio")
        duracion = int(request.POST.get("duracion_horas", 1))
        try:
            ReservaIndumentariaService().crear_reserva(indumentaria, hora_inicio, duracion)
        except ValueError as e:
            items = Indumentaria.objects.all()
            reservas_activas = ReservaIndumentaria.objects.filter(activa=True).select_related("indumentaria")
            return render(request, "Reservas/reservar_indumentaria.html", {
                "items": items, "reservas_activas": reservas_activas, "error": str(e),
            })
        return redirect("reservar_indumentaria")


class DevolverIndumentariaView(View):
    def post(self, request, reserva_id):
        reserva = get_object_or_404(ReservaIndumentaria, pk=reserva_id, activa=True)
        ReservaIndumentariaService().devolver_reserva(reserva)
        return redirect("reservar_indumentaria")