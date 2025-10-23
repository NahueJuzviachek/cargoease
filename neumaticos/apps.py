# neumaticos/apps.py
from django.apps import AppConfig

class NeumaticosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "neumaticos"

    def ready(self):
        # Registra receivers
        from . import signals  # noqa: F401
