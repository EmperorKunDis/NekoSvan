from django.urls import path
from rest_framework.routers import DefaultRouter

from .dashboard_views import DashboardView
from .views import DealActivityViewSet, DealViewSet, LeadFromDocumentView

router = DefaultRouter()
router.register("deals", DealViewSet)
router.register("deal-activities", DealActivityViewSet)

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("lead-from-document/", LeadFromDocumentView.as_view(), name="lead-from-document"),
] + router.urls
