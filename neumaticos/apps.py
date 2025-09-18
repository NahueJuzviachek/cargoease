# neumaticos/apps.py
from django.apps import AppConfig

class NeumaticosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "neumaticos"

    def ready(self):
        # Registra receivers (incluye el que escucha Viaje post_save)
        from . import signals  # noqa: F401
