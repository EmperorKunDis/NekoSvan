from rest_framework.routers import DefaultRouter

from .views import QuestionnaireResponseViewSet

router = DefaultRouter()
router.register("questionnaires", QuestionnaireResponseViewSet)

urlpatterns = router.urls
