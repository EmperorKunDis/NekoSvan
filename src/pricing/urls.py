from rest_framework.routers import DefaultRouter

from .views import PricingMatrixViewSet, PricingModifierViewSet, ProposalViewSet

router = DefaultRouter()
router.register("proposals", ProposalViewSet)
router.register("pricing-matrix", PricingMatrixViewSet)
router.register("pricing-modifiers", PricingModifierViewSet)

urlpatterns = router.urls
