from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class ViajesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "viajes"

    def ready(self):
        # Carga señales y deja un log para verificar que realmente se cargaron
        from . import signals  # noqa
        logger.info(">> Viajes: señales cargadas")
        print(">> Viajes: señales cargadas")  # visible en la consola del runserver