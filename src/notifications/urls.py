from django.urls import path
from rest_framework.routers import DefaultRouter

from .sse_views import NotificationSSEView
from .views import NotificationViewSet

router = DefaultRouter()
router.register("notifications", NotificationViewSet, basename="notification")

urlpatterns = [
    path("stream/", NotificationSSEView.as_view(), name="notification-stream"),
] + router.urls
