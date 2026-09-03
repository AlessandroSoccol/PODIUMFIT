# Reservas/domain/reglas.py
"""
Reglas de dominio puras (sin HTTP, sin serializers). Aqui vive el
conocimiento de negocio que antes estaba disperso; el Builder y el Service
las reutilizan.
"""
from django.utils import timezone

DURACION_MAXIMA_ESPACIO_HORAS = 1
DURACION_MAXIMA_INDUMENTARIA_HORAS = 2

# Máximo de unidades permitidas por reserva, según el tipo de indumentaria.
# Un tipo ausente de este diccionario solo queda limitado por el stock.
LIMITES_CANTIDAD_INDUMENTARIA = {
    "balon": 1,
    "pelota_tenis": 3,
    "pelota_ping_pong": 3,
    "raqueta": 4,
}


def limite_cantidad_para_tipo(tipo):
    return LIMITES_CANTIDAD_INDUMENTARIA.get(tipo)


def validar_cantidad_indumentaria(indumentaria, cantidad):
    if cantidad < 1:
        raise ValueError("La cantidad debe ser al menos 1.")
    limite = limite_cantidad_para_tipo(indumentaria.tipo)
    if limite is not None and cantidad > limite:
        raise ValueError(
            f"Máximo {limite} unidad(es) permitidas para {indumentaria.get_tipo_display()}."
        )
    if cantidad > indumentaria.stock:
        raise ValueError("No hay stock suficiente para la cantidad solicitada.")


def hay_bloqueo_de_espacios(excluir_espacio=None):
    """True si existe OTRA reserva de espacio activa y vigente en este momento,
    lo que bloquea la reserva de cualquier espacio distinto."""
    from Reservas.models import ReservaEspacio

    qs = ReservaEspacio.objects.filter(activa=True, fin__gt=timezone.now())
    if excluir_espacio is not None:
        qs = qs.exclude(espacio=excluir_espacio)
    return qs.exists()


def espacio_que_bloquea():
    """Devuelve el Espacio que actualmente mantiene el bloqueo global (o None)."""
    from Reservas.models import ReservaEspacio

    reserva = (
        ReservaEspacio.objects.filter(activa=True, fin__gt=timezone.now())
        .select_related("espacio")
        .order_by("-creado_en")
        .first()
    )
    return reserva.espacio if reserva else None


def validar_disponibilidad_global_espacio(espacio):
    if hay_bloqueo_de_espacios(excluir_espacio=espacio):
        raise ValueError(
            "Hay otro espacio reservado en este momento. Debes esperar a que "
            f"finalice su tiempo (máx. {DURACION_MAXIMA_ESPACIO_HORAS} hora) para reservar otro."
        )