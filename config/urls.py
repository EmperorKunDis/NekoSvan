from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from src.health.views import HealthCheckView

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("admin/", admin.site.urls),
    # API docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # API v1
    path("api/v1/accounts/", include("src.accounts.urls")),
    path("api/v1/pipeline/", include("src.pipeline.urls")),
    path("api/v1/questionnaire/", include("src.questionnaire.urls")),
    path("api/v1/pricing/", include("src.pricing.urls")),
    path("api/v1/contracts/", include("src.contracts.urls")),
    path("api/v1/projects/", include("src.projects.urls")),
    path("api/v1/notifications/", include("src.notifications.urls")),
    path("api/v1/documents/", include("src.documents.urls")),
    path("api/v1/companies/", include("src.companies.urls")),
    # Client portal (public, token-based)
    path("portal/", include("src.client_portal.urls")),
    path("api/v1/portal/", include("src.client_portal.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve media in production (needed for ONLYOFFICE)
from django.views.static import serve
from django.urls import re_path
urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
