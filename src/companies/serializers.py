from rest_framework import serializers

from .models import Communication, Company, CompanyContact, CompanyDocument


class CompanyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyContact
        fields = (
            "id",
            "company",
            "name",
            "position",
            "email",
            "phone",
            "is_primary",
            "notes",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class CommunicationSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    contact_name = serializers.CharField(source="contact.name", read_only=True)
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = Communication
        fields = (
            "id",
            "company",
            "contact",
            "contact_name",
            "type",
            "type_display",
            "subject",
            "content",
            "date",
            "created_by",
            "created_by_name",
            "created_at",
        )
        read_only_fields = ("id", "created_by", "created_at")


class CompanyDocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source="uploaded_by.get_full_name", read_only=True)

    class Meta:
        model = CompanyDocument
        fields = (
            "id",
            "company",
            "name",
            "file",
            "document_type",
            "uploaded_by",
            "uploaded_by_name",
            "created_at",
        )
        read_only_fields = ("id", "uploaded_by", "created_at")


class CompanyListSerializer(serializers.ModelSerializer):
    """Simplified serializer for company list views."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    contacts_count = serializers.IntegerField(source="contacts.count", read_only=True)
    deals_count = serializers.IntegerField(source="deals.count", read_only=True)

    class Meta:
        model = Company
        fields = (
            "id",
            "name",
            "ico",
            "dic",
            "email",
            "phone",
            "city",
            "status",
            "status_display",
            "sector",
            "tags",
            "contacts_count",
            "deals_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class CompanyDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with nested contacts and recent communications."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    contacts = CompanyContactSerializer(many=True, read_only=True)
    recent_communications = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = (
            "id",
            "name",
            "ico",
            "dic",
            "address",
            "city",
            "postal_code",
            "country",
            "email",
            "phone",
            "website",
            "status",
            "status_display",
            "sector",
            "tags",
            "notes",
            "contacts",
            "recent_communications",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_recent_communications(self, obj):
        recent = obj.communications.all()[:5]
        return CommunicationSerializer(recent, many=True).data


class CompanyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new company."""

    class Meta:
        model = Company
        fields = (
            "name",
            "ico",
            "dic",
            "address",
            "city",
            "postal_code",
            "country",
            "email",
            "phone",
            "website",
            "status",
            "sector",
            "tags",
            "notes",
        )


class CompanyCreateDealSerializer(serializers.Serializer):
    """Serializer for creating a deal from a company."""

    description = serializers.CharField(required=False, allow_blank=True)
    client_contact_name = serializers.CharField(required=True)
    client_email = serializers.EmailField(required=True)
    client_phone = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        from src.pipeline.models import Deal

        company = self.context["company"]

        deal = Deal.objects.create(
            company=company,
            client_company=company.name,
            client_contact_name=validated_data["client_contact_name"],
            client_email=validated_data["client_email"],
            client_phone=validated_data.get("client_phone", ""),
            client_ico=company.ico,
            description=validated_data.get("description", ""),
            created_by=self.context["request"].user,
        )

        return deal
