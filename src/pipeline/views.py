from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from src.accounts.permissions import DealPhasePermission, IsInternalUser
from src.notifications.services import notify_deal_created

from . import document_service, services
from .models import Deal, DealActivity, LeadDocument
from .serializers import (
    DealActivitySerializer,
    DealCreateSerializer,
    DealSerializer,
    LeadDocumentSerializer,
    PhaseAdvanceSerializer,
    RevisionRequestSerializer,
)


class DealViewSet(viewsets.ModelViewSet):
    queryset = Deal.objects.select_related("assigned_to", "created_by").all()
    permission_classes = [IsInternalUser, DealPhasePermission]
    filterset_fields = ("phase", "status", "assigned_to")
    search_fields = ("client_company", "client_contact_name", "client_email")
    ordering_fields = ("created_at", "updated_at", "phase_changed_at")

    def destroy(self, request, *args, **kwargs):
        """Delete a deal (soft delete - archive)."""
        deal = self.get_object()
        deal.status = Deal.Status.ARCHIVED
        deal.save(update_fields=["status"])
        DealActivity.objects.create(
            deal=deal,
            user=request.user,
            action="deal_archived",
            note="Deal archived/deleted",
        )
        return Response({"status": "archived"})

    def get_serializer_class(self):
        if self.action == "create":
            return DealCreateSerializer
        return DealSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        deal = serializer.save(created_by=request.user)
        notify_deal_created(deal)
        # Auto-advance from lead to qualification (assign to Vadim)
        services.advance_phase(deal, request.user, note="New lead created")
        deal.refresh_from_db()
        return Response(DealSerializer(deal).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def advance(self, request, pk=None):
        deal = self.get_object()
        ser = PhaseAdvanceSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            deal = services.advance_phase(deal, request.user, note=ser.validated_data["note"])
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(DealSerializer(deal).data)

    @action(detail=True, methods=["post"])
    def revision(self, request, pk=None):
        deal = self.get_object()
        ser = RevisionRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            deal = services.request_revision(deal, request.user, feedback=ser.validated_data["feedback"])
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(DealSerializer(deal).data)

    @action(detail=True, methods=["get"])
    def timeline(self, request, pk=None):
        deal = self.get_object()
        activities = deal.activities.select_related("user").all()
        return Response(DealActivitySerializer(activities, many=True).data)

    @action(detail=True, methods=["delete"], url_path="hard-delete")
    def hard_delete(self, request, pk=None):
        """Permanently delete a deal (admin only)."""
        deal = self.get_object()
        deal.delete()
        return Response({"status": "deleted"}, status=status.HTTP_204_NO_CONTENT)


class DealActivityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DealActivity.objects.select_related("deal", "user").all()
    serializer_class = DealActivitySerializer
    filterset_fields = ("deal",)


class LeadFromDocumentView(APIView):
    """Vytvoření leadu z dokumentu nebo textu."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = LeadDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Vytvořit dokument
        document = LeadDocument.objects.create(
            file=request.FILES.get("file"),
            raw_text=serializer.validated_data.get("raw_text", ""),
            document_type=serializer.validated_data.get(
                "document_type", LeadDocument.DocumentType.OTHER
            ),
            uploaded_by=request.user,
        )

        # Zpracovat
        deal = document_service.process_document(document, user=request.user)

        if deal:
            notify_deal_created(deal)
            services.advance_phase(deal, request.user, note="Lead z dokumentu")
            deal.refresh_from_db()
            return Response(
                {
                    "status": "success",
                    "deal": DealSerializer(deal).data,
                    "extracted_data": document.extracted_data,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {
                    "status": "error",
                    "error": document.error_message or "Nepodařilo se zpracovat dokument",
                    "extracted_data": document.extracted_data,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
