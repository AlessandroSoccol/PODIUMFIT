from celery import shared_task
import time

@shared_task
def procesar_reporte_asincrono(usuario_id):
    time.sleep(5)
    return f"Reporte procesado en segundo plano para el usuario {usuario_id}"
