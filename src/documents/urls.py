from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import DocumentViewSet, OnlyOfficeCallbackView

router = DefaultRouter()
router.register("documents", DocumentViewSet)

urlpatterns = [
    path("callback/", OnlyOfficeCallbackView.as_view(), name="onlyoffice-callback"),
] + router.urls
