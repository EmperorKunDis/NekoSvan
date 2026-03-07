from rest_framework.routers import DefaultRouter

from .views import ContractTemplateViewSet, ContractViewSet, PaymentViewSet

router = DefaultRouter()
router.register("contract-templates", ContractTemplateViewSet)
router.register("contracts", ContractViewSet)
router.register("payments", PaymentViewSet)

urlpatterns = router.urls
