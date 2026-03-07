from django.apps import AppConfig


class QuestionnaireConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "src.questionnaire"
    label = "questionnaire"
    verbose_name = "Questionnaire"
