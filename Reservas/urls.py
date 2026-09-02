# Reservas/urls.py
from django.urls import path
from .views import (
    IndexView, ReservarEspacioView, LiberarEspacioView,
    ReservarIndumentariaView, DevolverIndumentariaView,
)

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('espacio/reservar/', ReservarEspacioView.as_view(), name='reservar_espacio'),
    path('espacio/liberar/<int:reserva_id>/', LiberarEspacioView.as_view(), name='liberar_espacio'),
    path('indumentaria/reservar/', ReservarIndumentariaView.as_view(), name='reservar_indumentaria'),
    path('indumentaria/devolver/<int:reserva_id>/', DevolverIndumentariaView.as_view(), name='devolver_indumentaria'),
]