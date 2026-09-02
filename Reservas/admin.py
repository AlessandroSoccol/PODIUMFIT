from django.contrib import admin
from Reservas.models import Espacio, Indumentaria, ReservaEspacio, ReservaIndumentaria

admin.site.register(Espacio)
admin.site.register(Indumentaria)
admin.site.register(ReservaEspacio)
admin.site.register(ReservaIndumentaria)