# Reservas/models.py
from django.db import models


class Espacio(models.Model):
    nombre = models.CharField(max_length=100)
    cantidad_disponible = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.nombre


class Indumentaria(models.Model):
    nombre = models.CharField(max_length=100)
    talla = models.CharField(max_length=10)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} ({self.talla})"


class ReservaEspacio(models.Model):
    espacio = models.ForeignKey(Espacio, on_delete=models.CASCADE)
    hora_inicio = models.TimeField()
    duracion_horas = models.PositiveSmallIntegerField(default=1)
    activa = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.espacio.nombre} - {self.hora_inicio} ({self.duracion_horas}h)"


class ReservaIndumentaria(models.Model):
    indumentaria = models.ForeignKey(Indumentaria, on_delete=models.CASCADE)
    hora_inicio = models.TimeField()
    duracion_horas = models.PositiveSmallIntegerField(default=1)
    activa = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.indumentaria.nombre} - {self.hora_inicio} ({self.duracion_horas}h)"