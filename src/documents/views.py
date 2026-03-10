import json

from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from src.accounts.permissions import IsInternalUser

from .jwt_utils import generate_onlyoffice_token, verify_onlyoffice_token
from .models import Document, DocumentVersion
from .serializers import DocumentSerializer, DocumentVersionSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    """CRUD for documents."""

    queryset = Document.objects.select_related("created_by", "deal", "project")
    serializer_class = DocumentSerializer
    permission_classes = [IsInternalUser]
    parser_classes = [MultiPartParser, FormParser]
    filterset_fields = ("document_type", "deal", "project")

    def perform_create(self, serializer):
        file = self.request.FILES.get("file")
        file_type = "docx"
        if file:
            ext = file.name.split(".")[-1].lower()
            if ext in ["doc", "docx", "odt", "rtf", "txt"]:
                file_type = ext
            elif ext in ["xls", "xlsx", "ods", "csv"]:
                file_type = ext
            elif ext in ["ppt", "pptx", "odp"]:
                file_type = ext
            elif ext == "pdf":
                file_type = "pdf"
        serializer.save(created_by=self.request.user, file_type=file_type)

    def perform_update(self, serializer):
        serializer.save(last_modified_by=self.request.user)

    @action(detail=True, methods=["get"])
    def onlyoffice_config(self, request, pk=None):
        """Get ONLYOFFICE configuration for this document."""
        document = self.get_object()
        config = get_onlyoffice_config(document, request.user, request)
        return Response(config)

    @action(detail=True, methods=["get"])
    def versions(self, request, pk=None):
        """Get version history."""
        document = self.get_object()
        versions = document.versions.select_related("created_by")
        return Response(DocumentVersionSerializer(versions, many=True).data)

    @action(detail=True, methods=["post"])
    def regenerate_key(self, request, pk=None):
        """Regenerate document key to force reload."""
        document = self.get_object()
        document.regenerate_key()
        return Response({"key": document.key})


def get_onlyoffice_config(document: Document, user, request) -> dict:
    """Generate ONLYOFFICE Document Server configuration."""
    # Get the public domain from request
    # ONLYOFFICE needs a publicly accessible URL to download the document
    host = request.get_host() if request else "posthub.work"
    protocol = "https"  # Always use HTTPS (Cloudflare terminates SSL)

    # Document URL - must be publicly accessible for ONLYOFFICE to download
    document_url = f"{protocol}://{host}/app/media/{document.file.name}"

    # Callback URL for saving - internal Docker network URL
    callback_url = "http://apiserver:8000/api/v1/documents/callback/"

    doc_type_map = {
        "docx": "word",
        "doc": "word",
        "odt": "word",
        "rtf": "word",
        "txt": "word",
        "xlsx": "cell",
        "xls": "cell",
        "ods": "cell",
        "csv": "cell",
        "pptx": "slide",
        "ppt": "slide",
        "odp": "slide",
        "pdf": "word",
    }

    document_type = doc_type_map.get(document.file_type, "word")

    config = {
        "document": {
            "fileType": document.file_type,
            "key": document.key,
            "title": document.title,
            "url": document_url,
        },
        "documentType": document_type,
        "editorConfig": {
            "callbackUrl": callback_url,
            "lang": "cs",
            "mode": "edit",
            "user": {
                "id": str(user.id),
                "name": user.get_full_name() or user.username,
            },
            "customization": {
                "autosave": True,
                "chat": False,
                "commentAuthorOnly": False,
                "comments": True,
                "compactHeader": True,
                "compactToolbar": False,
                "feedback": False,
                "forcesave": True,
                "help": False,
                "hideRightMenu": False,
                "logo": {
                    "image": "",
                    "imageEmbedded": "",
                    "url": "https://praut.cz",
                },
                "reviewDisplay": "markup",
                "showReviewChanges": True,
                "zoom": 100,
            },
        },
        "height": "100%",
        "width": "100%",
    }

    token = generate_onlyoffice_token(config)
    if token:
        config["token"] = token

    return config


class OnlyOfficeCallbackView(APIView):
    """Callback endpoint for ONLYOFFICE Document Server."""

    authentication_classes = []  # No auth - ONLYOFFICE calls this internally
    permission_classes = []  # ONLYOFFICE calls this without auth

    def post(self, request):
        """Handle ONLYOFFICE callback."""
        # Verify JWT if secret is configured
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            payload = verify_onlyoffice_token(token)
            if payload is None:
                return JsonResponse({"error": 1})
        else:
            # No auth header — check if JWT is required
            payload = verify_onlyoffice_token("")
            if payload is None:
                return JsonResponse({"error": 1})

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": 1})

        status_code = body.get("status")
        key = body.get("key")
        url = body.get("url")

        # Status codes:
        # 0 - no document with key found
        # 1 - document is being edited
        # 2 - document is ready for saving
        # 3 - document saving error
        # 4 - document closed with no changes
        # 6 - document is being edited, but current state saved
        # 7 - error force saving document

        if status_code in [2, 6]:  # Ready for saving or force save
            if key and url:
                try:
                    document = Document.objects.get(key=key)
                    # Download and save the document
                    import requests

                    response = requests.get(url, timeout=30)
                    if response.status_code == 200:
                        # Save new version
                        version_num = document.versions.count() + 1
                        from django.core.files.base import ContentFile

                        version = DocumentVersion.objects.create(
                            document=document,
                            version=version_num,
                            changes_description="Auto-saved from ONLYOFFICE",
                        )
                        version.file.save(
                            f"{document.title}_v{version_num}.{document.file_type}",
                            ContentFile(response.content),
                        )

                        # Update main document file
                        document.file.save(
                            f"{document.title}.{document.file_type}",
                            ContentFile(response.content),
                        )
                        document.regenerate_key()
                except Document.DoesNotExist:
                    pass
                except Exception as e:
                    print(f"ONLYOFFICE callback error: {e}")

        return JsonResponse({"error": 0})
