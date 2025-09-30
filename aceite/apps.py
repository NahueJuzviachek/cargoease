# aceite/apps.py
from django.apps import AppConfig

class AceiteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "aceite"

    def ready(self):
        from django.db.models.signals import post_save, post_delete
        from . import signals
        try:
            from viajes.models import Viaje
            post_save.connect(
                signals.aceite_recalc_on_viaje_save,
                sender=Viaje,
                dispatch_uid="aceite_recalc_on_viaje_save",
            )
            post_delete.connect(
                signals.aceite_recalc_on_viaje_delete,
                sender=Viaje,
                dispatch_uid="aceite_recalc_on_viaje_delete",
            )
        except Exception:
            # En migraciones iniciales puede no estar 'viajes'
            pass
