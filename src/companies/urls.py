from rest_framework.routers import DefaultRouter

from .views import CommunicationViewSet, CompanyContactViewSet, CompanyDocumentViewSet, CompanyViewSet

router = DefaultRouter()
router.register("companies", CompanyViewSet, basename="company")
router.register("contacts", CompanyContactViewSet, basename="company-contact")
router.register("communications", CommunicationViewSet, basename="communication")
router.register("documents", CompanyDocumentViewSet, basename="company-document")

urlpatterns = router.urls
