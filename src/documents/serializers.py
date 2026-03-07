from rest_framework import serializers

from .models import Document, DocumentVersion


class DocumentSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True
    )
    document_type_display = serializers.CharField(
        source="get_document_type_display", read_only=True
    )
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = (
            "id",
            "title",
            "document_type",
            "document_type_display",
            "file",
            "file_url",
            "file_type",
            "deal",
            "project",
            "key",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "key", "created_by", "created_at", "updated_at")

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class DocumentVersionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True
    )

    class Meta:
        model = DocumentVersion
        fields = (
            "id",
            "document",
            "version",
            "file",
            "created_by",
            "created_by_name",
            "created_at",
            "changes_description",
        )
        read_only_fields = ("id", "created_by", "created_at")


class OnlyOfficeConfigSerializer(serializers.Serializer):
    """Serializer for ONLYOFFICE Document Server configuration."""

    document_server_url = serializers.CharField()
    document = serializers.DictField()
    editor_config = serializers.DictField()
