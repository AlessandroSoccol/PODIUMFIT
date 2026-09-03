import os
import sys

from django.apps import AppConfig


class CuentasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Cuentas"

    def ready(self):
        """Cada vez que se ejecuta el programa (se levanta el servidor) se
        cierra la sesión de todos los usuarios, para que cualquiera que
        entre deba volver a iniciar sesión. Esto solo corre al arrancar
        'runserver', no en otros comandos de manage.py (migrate, test, etc.)."""
        if "runserver" not in sys.argv:
            return

        # Con el auto-reloader de Django el proceso "vigía" también llama a
        # ready(); solo el proceso que realmente sirve peticiones (o el
        # arranque con --noreload) debe limpiar las sesiones.
        if os.environ.get("RUN_MAIN") != "true" and "--noreload" not in sys.argv:
            return

        from django.contrib.sessions.models import Session
        from django.db.utils import OperationalError, ProgrammingError

        try:
            Session.objects.all().delete()
        except (OperationalError, ProgrammingError):
            # La tabla de sesiones aún no existe (falta correr migrate); se ignora.
            pass
