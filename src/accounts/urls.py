from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ChangePasswordView,
    CompanyViewSet,
    CsrfTokenView,
    LoginView,
    LogoutView,
    ProfileView,
    TeamMemberDetailView,
    TeamView,
    UserViewSet,
)

router = DefaultRouter()
router.register("users", UserViewSet)
router.register("companies", CompanyViewSet)

urlpatterns = [
    path("login/", LoginView.as_view(), name="api-login"),
    path("logout/", LogoutView.as_view(), name="api-logout"),
    path("csrf/", CsrfTokenView.as_view(), name="api-csrf"),
    # Profile management
    path("profile/", ProfileView.as_view(), name="api-profile"),
    path("profile/password/", ChangePasswordView.as_view(), name="api-change-password"),
    # Team management (for masters)
    path("team/", TeamView.as_view(), name="api-team"),
    path("team/<int:pk>/", TeamMemberDetailView.as_view(), name="api-team-member"),
] + router.urls
