from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "src.notifications"
    label = "notifications"
    verbose_name = "Notifications"

    def ready(self):
        from src.pipeline.signals import deal_phase_changed

        from .receivers import notify_on_phase_change

        deal_phase_changed.connect(notify_on_phase_change)
