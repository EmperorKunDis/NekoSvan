from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from src.accounts.permissions import IsInternalUser
from src.notifications.services import notify_questionnaire_completed
from src.pipeline import services as pipeline_services
from src.pipeline.models import Deal

from .models import QuestionnaireResponse
from .serializers import AIExtractSerializer, QuestionnaireResponseSerializer
from .services import OllamaUnavailableError, extract_from_text, extract_text_from_file


class QuestionnaireResponseViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireResponse.objects.select_related(
        "deal", "filled_by"
    ).all()
    serializer_class = QuestionnaireResponseSerializer
    permission_classes = [IsInternalUser]
    filterset_fields = ("deal",)

    def perform_create(self, serializer):
        questionnaire = serializer.save(filled_by=self.request.user)
        _sync_to_deal(questionnaire)
        # Auto-advance deal from qualification to pricing
        deal = questionnaire.deal
        notify_questionnaire_completed(deal)
        if deal.phase == Deal.Phase.QUALIFICATION:
            pipeline_services.advance_phase(
                deal, self.request.user, note="Questionnaire completed"
            )

    def perform_update(self, serializer):
        questionnaire = serializer.save()
        _sync_to_deal(questionnaire)

    def create(self, request, *args, **kwargs):
        deal_id = request.data.get("deal")
        if deal_id and QuestionnaireResponse.objects.filter(deal_id=deal_id).exists():
            return Response(
                {"error": "Questionnaire already exists for this deal"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=["post"], url_path="ai-extract")
    def ai_extract(self, request):
        """Extract questionnaire data from text or file using local Ollama."""
        serializer = AIExtractSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        text = serializer.validated_data.get("text", "")
        uploaded_file = serializer.validated_data.get("file")

        if uploaded_file:
            file_text = extract_text_from_file(uploaded_file)
            text = f"{text}\n\n{file_text}" if text else file_text

        if not text.strip():
            return Response(
                {"error": "No text content could be extracted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            extracted = extract_from_text(text)
        except OllamaUnavailableError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response({"extracted": extracted})


def _sync_to_deal(questionnaire: QuestionnaireResponse) -> None:
    """Sync questionnaire fields A1-A5 back to Deal model."""
    deal = questionnaire.deal
    changed = False

    field_map = {
        "a_company_name": "client_company",
        "a_contact_person": "client_contact_name",
        "a_email": "client_email",
        "a_phone": "client_phone",
        "a_ico": "client_ico",
    }

    for q_field, d_field in field_map.items():
        value = getattr(questionnaire, q_field, "")
        if value and value != getattr(deal, d_field, ""):
            setattr(deal, d_field, value)
            changed = True

    if changed:
        update_fields = [
            d_field
            for q_field, d_field in field_map.items()
            if getattr(questionnaire, q_field, "")
        ]
        deal.save(update_fields=update_fields)
