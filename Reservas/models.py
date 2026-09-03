from django.db import models


class Espacio(models.Model):
    nombre = models.CharField(max_length=100)
    cantidad_disponible = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.nombre


class Indumentaria(models.Model):
    TIPO_BALON = "balon"
    TIPO_PELOTA_TENIS = "pelota_tenis"
    TIPO_PELOTA_PING_PONG = "pelota_ping_pong"
    TIPO_RAQUETA = "raqueta"
    TIPO_OTRO = "otro"

    TIPO_CHOICES = [
        (TIPO_BALON, "Balón"),
        (TIPO_PELOTA_TENIS, "Pelota de tenis"),
        (TIPO_PELOTA_PING_PONG, "Pelota de tenis de mesa"),
        (TIPO_RAQUETA, "Raqueta"),
        (TIPO_OTRO, "Otro"),
    ]

    nombre = models.CharField(max_length=100)
    talla = models.CharField(max_length=10, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default=TIPO_OTRO)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} ({self.talla})" if self.talla else self.nombre


class ReservaEspacio(models.Model):
    espacio = models.ForeignKey(Espacio, on_delete=models.CASCADE)
    hora_inicio = models.TimeField()
    duracion_horas = models.PositiveSmallIntegerField(default=1)
    fin = models.DateTimeField(null=True, blank=True)
    activa = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.espacio.nombre} - {self.hora_inicio} ({self.duracion_horas}h)"


class ReservaIndumentaria(models.Model):
    indumentaria = models.ForeignKey(Indumentaria, on_delete=models.CASCADE)
    hora_inicio = models.TimeField()
    duracion_horas = models.PositiveSmallIntegerField(default=1)
    cantidad = models.PositiveSmallIntegerField(default=1)
    fin = models.DateTimeField(null=True, blank=True)
    activa = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cantidad}x {self.indumentaria.nombre} - {self.hora_inicio} ({self.duracion_horas}h)"