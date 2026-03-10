from rest_framework import serializers

from .models import ClientCompany, Deal, DealActivity, LeadDocument


class ClientCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientCompany
        fields = ("id", "name", "contact_name", "email", "phone", "ico", "address", "notes", "created_at")
        read_only_fields = ("id", "created_at")


class DealSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source="assigned_to.get_full_name", read_only=True)
    phase_display = serializers.CharField(source="get_phase_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    client_data = serializers.SerializerMethodField()

    class Meta:
        model = Deal
        fields = (
            "id",
            "client",
            "client_company",
            "client_contact_name",
            "client_email",
            "client_phone",
            "client_data",
            "description",
            "phase",
            "phase_display",
            "status",
            "status_display",
            "assigned_to",
            "assigned_to_name",
            "revision_count",
            "portal_token",
            "created_at",
            "updated_at",
            "phase_changed_at",
            "created_by",
        )
        read_only_fields = ("id", "phase", "status", "assigned_to", "revision_count", "portal_token", "created_by")

    def get_client_data(self, obj):
        return obj.get_client_data()


class DealCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = (
            "client_company",
            "client_contact_name",
            "client_email",
            "client_phone",
            "description",
        )


class DealActivitySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = DealActivity
        fields = ("id", "deal", "user", "user_name", "action", "note", "created_at")
        read_only_fields = ("id", "user", "created_at")


class PhaseAdvanceSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, default="")


class RevisionRequestSerializer(serializers.Serializer):
    feedback = serializers.CharField()


class LeadDocumentSerializer(serializers.Serializer):
    """Serializer pro vytvoření leadu z dokumentu."""

    file = serializers.FileField(
        required=False,
        allow_null=True,
        help_text="Soubor (TXT, PDF, DOC, DOCX, EML)",
        error_messages={
            "invalid": "Nahraný soubor je neplatný. Podporované formáty: TXT, PDF, DOC, DOCX, EML.",
            "empty": "Nahraný soubor je prázdný.",
        },
    )
    raw_text = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Vložený text (pokud není soubor)",
        error_messages={
            "invalid": "Text musí být validní řetězec.",
        },
    )
    document_type = serializers.ChoiceField(
        choices=LeadDocument.DocumentType.choices,
        required=False,
        default=LeadDocument.DocumentType.OTHER,
        error_messages={
            "invalid_choice": "Neplatný typ dokumentu. Povolené hodnoty: {choices}.",
        },
    )

    def validate(self, attrs):
        file = attrs.get("file")
        raw_text = attrs.get("raw_text", "").strip()

        if not file and not raw_text:
            raise serializers.ValidationError({
                "file": "Musíte nahrát soubor nebo vložit text.",
                "raw_text": "Musíte nahrát soubor nebo vložit text.",
            })

        # Validace formátu souboru
        if file:
            allowed_extensions = [".txt", ".pdf", ".doc", ".docx", ".eml"]
            file_name = file.name.lower()
            if not any(file_name.endswith(ext) for ext in allowed_extensions):
                raise serializers.ValidationError({
                    "file": f"Nepodporovaný formát souboru. Povolené: {', '.join(allowed_extensions)}"
                })

        return attrs
