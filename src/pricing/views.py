from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from src.accounts.permissions import IsInternalUser, IsMartinRole, ProposalPermission
from src.notifications.services import trigger_n8n_webhook
from src.pipeline import services as pipeline_services
from src.pipeline.models import Deal
from src.questionnaire.models import QuestionnaireResponse

from . import services
from .models import PricingMatrix, PricingModifier, Proposal
from .serializers import PricingMatrixSerializer, PricingModifierSerializer, ProposalSerializer


class PricingMatrixViewSet(viewsets.ModelViewSet):
    """Pricing matrix management — only Martin can edit."""

    queryset = PricingMatrix.objects.filter(is_active=True)
    serializer_class = PricingMatrixSerializer
    permission_classes = [IsInternalUser, IsMartinRole]
    filterset_fields = ("category", "is_active")


class PricingModifierViewSet(viewsets.ModelViewSet):
    """Pricing modifiers management — only Martin can edit."""

    queryset = PricingModifier.objects.filter(is_active=True)
    serializer_class = PricingModifierSerializer
    permission_classes = [IsInternalUser, IsMartinRole]
    filterset_fields = ("modifier_type", "is_active")


class ProposalViewSet(viewsets.ModelViewSet):
    queryset = Proposal.objects.select_related("deal", "created_by").all()
    serializer_class = ProposalSerializer
    permission_classes = [IsInternalUser, ProposalPermission]
    filterset_fields = ("deal", "status", "version")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=["get"], url_path="auto-calculate/(?P<deal_id>[0-9]+)")
    def auto_calculate(self, request, deal_id=None):
        """Get auto-calculated pricing for a deal based on its questionnaire."""
        try:
            questionnaire = QuestionnaireResponse.objects.get(deal_id=deal_id)
        except QuestionnaireResponse.DoesNotExist:
            return Response({"error": "Questionnaire not found for this deal"}, status=404)

        result = services.calculate_proposal(questionnaire)
        return Response(result)

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        """Mark proposal as sent and advance deal to presentation phase."""
        proposal = self.get_object()
        proposal.status = Proposal.Status.SENT
        proposal.save(update_fields=["status", "updated_at"])

        deal = proposal.deal

        # Trigger N8N webhook — email client with portal link
        trigger_n8n_webhook("proposal.sent", {
            "deal_id": deal.id,
            "client_company": deal.client_company,
            "client_email": deal.client_email,
            "portal_token": str(deal.portal_token),
            "total_price": str(proposal.total_price),
            "proposal_version": proposal.version,
        })

        if deal.phase == Deal.Phase.PRICING:
            pipeline_services.advance_phase(deal, request.user, note=f"Proposal v{proposal.version} sent")

        return Response(ProposalSerializer(proposal).data)
