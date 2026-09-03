from django.test import TestCase

# Create your tests here.
from django.test import TestCase

from Reservas.domain import reglas
from Reservas.domain.builders import ReservaIndumentariaBuilder
from Reservas.models import Indumentaria


class LimiteCantidadIndumentariaTests(TestCase):
    """Fija la regla de negocio: máximo de unidades por tipo en una misma reserva.

    - balón: 1
    - pelota de tenis: 3
    - pelota de tenis de mesa: 3
    - raqueta (tenis o tenis de mesa): 4
    """

    def _crear(self, tipo, stock=10):
        return Indumentaria.objects.create(nombre=f"Item {tipo}", tipo=tipo, stock=stock)

    def test_limites_configurados(self):
        self.assertEqual(reglas.limite_cantidad_para_tipo(Indumentaria.TIPO_BALON), 1)
        self.assertEqual(reglas.limite_cantidad_para_tipo(Indumentaria.TIPO_PELOTA_TENIS), 3)
        self.assertEqual(reglas.limite_cantidad_para_tipo(Indumentaria.TIPO_PELOTA_PING_PONG), 3)
        self.assertEqual(reglas.limite_cantidad_para_tipo(Indumentaria.TIPO_RAQUETA), 4)

    def test_balon_permite_uno_pero_no_dos(self):
        balon = self._crear(Indumentaria.TIPO_BALON)
        reglas.validar_cantidad_indumentaria(balon, 1)  # no lanza
        with self.assertRaises(ValueError):
            reglas.validar_cantidad_indumentaria(balon, 2)

    def test_pelota_tenis_permite_tres_pero_no_cuatro(self):
        pelota = self._crear(Indumentaria.TIPO_PELOTA_TENIS)
        reglas.validar_cantidad_indumentaria(pelota, 3)
        with self.assertRaises(ValueError):
            reglas.validar_cantidad_indumentaria(pelota, 4)

    def test_pelota_ping_pong_permite_tres_pero_no_cuatro(self):
        pelota = self._crear(Indumentaria.TIPO_PELOTA_PING_PONG)
        reglas.validar_cantidad_indumentaria(pelota, 3)
        with self.assertRaises(ValueError):
            reglas.validar_cantidad_indumentaria(pelota, 4)

    def test_raqueta_permite_cuatro_pero_no_cinco(self):
        raqueta = self._crear(Indumentaria.TIPO_RAQUETA)
        reglas.validar_cantidad_indumentaria(raqueta, 4)
        with self.assertRaises(ValueError):
            reglas.validar_cantidad_indumentaria(raqueta, 5)

    def test_builder_respeta_el_limite_de_principio_a_fin(self):
        balon = self._crear(Indumentaria.TIPO_BALON)
        with self.assertRaises(ValueError):
            (
                ReservaIndumentariaBuilder()
                .de_indumentaria(balon)
                .a_las("10:00")
                .con_cantidad(2)
                .build()
            )
