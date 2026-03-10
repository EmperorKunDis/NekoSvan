from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "src.projects"
    label = "projects"
    verbose_name = "Projects"

    def ready(self):
        from src.pipeline.signals import deal_phase_changed

        from .receivers import auto_create_project

        deal_phase_changed.connect(auto_create_project)
