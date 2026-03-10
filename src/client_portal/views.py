from django.http import FileResponse
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from src.contracts.models import Contract
from src.notifications.services import notify_milestone_approved, notify_proposal_accepted, notify_proposal_rejected
from src.pipeline import services as pipeline_services
from src.pipeline.models import Deal
from src.projects import services as project_services
from src.projects.models import Milestone

from .serializers import (
    ClientFeedbackSerializer,
    PortalContractSerializer,
    PortalDealSerializer,
    PortalPaymentSerializer,
    PortalProjectSerializer,
    PortalProposalSerializer,
)
from .services import log_portal_access
from .throttles import PortalReadThrottle, PortalWriteThrottle


def get_deal_by_token(token: str) -> Deal | None:
    try:
        deal = Deal.objects.get(portal_token=token)
    except (Deal.DoesNotExist, ValueError):
        return None
    if not deal.is_portal_token_valid():
        return None
    return deal


class PortalDashboardView(APIView):
    """Client portal dashboard — overview of deal, proposal, project."""

    permission_classes = [AllowAny]
    throttle_classes = [PortalReadThrottle]

    def get(self, request, token):
        deal = get_deal_by_token(token)
        if not deal:
            return Response({"error": "Invalid token"}, status=status.HTTP_404_NOT_FOUND)
        log_portal_access(deal, request, "dashboard_view")

        data = {
            "deal": PortalDealSerializer(deal).data,
            "proposal": None,
            "contract": None,
            "payments": [],
            "project": None,
        }

        # Latest sent/accepted proposal
        proposal = deal.proposals.filter(status__in=["sent", "accepted"]).order_by("-version").first()
        if proposal:
            data["proposal"] = PortalProposalSerializer(proposal).data

        # Contract
        if hasattr(deal, "contract"):
            data["contract"] = PortalContractSerializer(deal.contract).data

        # Payments
        data["payments"] = PortalPaymentSerializer(deal.payments.all(), many=True).data

        # Project
        if hasattr(deal, "project"):
            data["project"] = PortalProjectSerializer(deal.project).data

        return Response(data)


class PortalProposalAcceptView(APIView):
    """Client accepts a proposal."""

    permission_classes = [AllowAny]
    throttle_classes = [PortalWriteThrottle]

    def post(self, request, token):
        deal = get_deal_by_token(token)
        if not deal:
            return Response({"error": "Invalid token"}, status=status.HTTP_404_NOT_FOUND)
        log_portal_access(deal, request, "proposal_accept")

        proposal = deal.proposals.filter(status="sent").order_by("-version").first()
        if not proposal:
            return Response({"error": "No proposal to accept"}, status=status.HTTP_400_BAD_REQUEST)

        proposal.status = "accepted"
        proposal.save(update_fields=["status", "updated_at"])
        notify_proposal_accepted(deal)

        if deal.phase == Deal.Phase.PRESENTATION:
            pipeline_services.advance_phase(deal, user=None, note="Client accepted proposal via portal")

        return Response({"status": "accepted"})


class PortalProposalRejectView(APIView):
    """Client requests revision on a proposal."""

    permission_classes = [AllowAny]
    throttle_classes = [PortalWriteThrottle]

    def post(self, request, token):
        deal = get_deal_by_token(token)
        if not deal:
            return Response({"error": "Invalid token"}, status=status.HTTP_404_NOT_FOUND)
        log_portal_access(deal, request, "proposal_reject")

        ser = ClientFeedbackSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        proposal = deal.proposals.filter(status="sent").order_by("-version").first()
        if not proposal:
            return Response({"error": "No proposal to reject"}, status=status.HTTP_400_BAD_REQUEST)

        proposal.client_feedback = ser.validated_data["feedback"]
        proposal.status = "rejected"
        proposal.save(update_fields=["status", "client_feedback", "updated_at"])
        notify_proposal_rejected(deal, feedback=ser.validated_data["feedback"])

        if deal.phase == Deal.Phase.PRESENTATION:
            pipeline_services.request_revision(deal, user=None, feedback=ser.validated_data["feedback"])

        return Response({"status": "revision_requested"})


class PortalMilestoneApproveView(APIView):
    """Client approves a milestone."""

    permission_classes = [AllowAny]
    throttle_classes = [PortalWriteThrottle]

    def post(self, request, token, milestone_id):
        deal = get_deal_by_token(token)
        if not deal:
            return Response({"error": "Invalid token"}, status=status.HTTP_404_NOT_FOUND)
        log_portal_access(deal, request, "milestone_approve")

        try:
            milestone = Milestone.objects.get(
                id=milestone_id,
                project__deal=deal,
                status=Milestone.Status.CLIENT_REVIEW,
            )
        except Milestone.DoesNotExist:
            return Response({"error": "Milestone not found or not in review"}, status=status.HTTP_404_NOT_FOUND)

        milestone = project_services.client_approve_milestone(milestone)
        notify_milestone_approved(milestone)
        return Response({"status": "approved"})


class PortalMilestoneRejectView(APIView):
    """Client rejects a milestone with feedback."""

    permission_classes = [AllowAny]
    throttle_classes = [PortalWriteThrottle]

    def post(self, request, token, milestone_id):
        deal = get_deal_by_token(token)
        if not deal:
            return Response({"error": "Invalid token"}, status=status.HTTP_404_NOT_FOUND)
        log_portal_access(deal, request, "milestone_reject")

        ser = ClientFeedbackSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        try:
            milestone = Milestone.objects.get(
                id=milestone_id,
                project__deal=deal,
                status=Milestone.Status.CLIENT_REVIEW,
            )
        except Milestone.DoesNotExist:
            return Response({"error": "Milestone not found or not in review"}, status=status.HTTP_404_NOT_FOUND)

        milestone = project_services.client_reject_milestone(milestone, ser.validated_data["feedback"])
        return Response({"status": "rejected"})


class PortalContractDownloadView(APIView):
    """Client downloads contract PDF."""

    permission_classes = [AllowAny]
    throttle_classes = [PortalReadThrottle]

    def get(self, request, token):
        deal = get_deal_by_token(token)
        if not deal:
            return Response({"error": "Invalid token"}, status=status.HTTP_404_NOT_FOUND)
        log_portal_access(deal, request, "contract_download")

        try:
            contract = Contract.objects.get(deal=deal)
        except Contract.DoesNotExist:
            return Response({"error": "No contract found"}, status=status.HTTP_404_NOT_FOUND)

        if not contract.generated_pdf:
            return Response({"error": "PDF not yet generated"}, status=status.HTTP_404_NOT_FOUND)

        return FileResponse(
            contract.generated_pdf.open("rb"),
            content_type="application/pdf",
            as_attachment=True,
            filename=f"smlouva-{deal.client_company}.pdf",
        )
