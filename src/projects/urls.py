from rest_framework.routers import DefaultRouter

from .views import (
    MilestoneTemplateViewSet,
    MilestoneViewSet,
    ProjectCommentViewSet,
    ProjectViewSet,
    QAChecklistViewSet,
    TemplateCommentViewSet,
)

router = DefaultRouter()
router.register("projects", ProjectViewSet)
router.register("milestones", MilestoneViewSet)
router.register("milestone-templates", MilestoneTemplateViewSet)
router.register("qa-checklists", QAChecklistViewSet)
router.register("project-comments", ProjectCommentViewSet)
router.register("template-comments", TemplateCommentViewSet)

urlpatterns = router.urls
