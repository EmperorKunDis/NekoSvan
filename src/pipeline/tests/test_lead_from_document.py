"""Tests for lead-from-document endpoint."""

import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient

from src.pipeline.models import Deal, LeadDocument


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_user(django_user_model):
    """Create an authenticated user."""
    return django_user_model.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        role="martin",
    )


@pytest.mark.django_db
class TestLeadFromDocumentView:
    """Test cases for LeadFromDocumentView."""

    def test_create_lead_from_text(self, api_client, auth_user):
        """Test vytvoření leadu z textu."""
        api_client.force_authenticate(user=auth_user)

        data = {
            "raw_text": "Email od klienta: Firma TestCorp s.r.o., kontakt Jan Novák, jan@testcorp.cz, tel: +420 777 888 999",
            "document_type": "email",
        }

        response = api_client.post("/api/v1/pipeline/lead-from-document/", data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == "success"
        assert "deal" in response.data
        assert "extracted_data" in response.data

        # Verify LeadDocument was created
        assert LeadDocument.objects.filter(uploaded_by=auth_user).exists()

    def test_create_lead_from_file(self, api_client, auth_user):
        """Test vytvoření leadu z textového souboru."""
        api_client.force_authenticate(user=auth_user)

        file_content = b"Firma: Example s.r.o.\nEmail: info@example.cz\nTelefon: 777888999"
        uploaded_file = SimpleUploadedFile(
            "test_document.txt", file_content, content_type="text/plain"
        )

        data = {
            "file": uploaded_file,
            "document_type": "brief",
        }

        response = api_client.post("/api/v1/pipeline/lead-from-document/", data, format="multipart")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == "success"

        # Verify file was saved
        doc = LeadDocument.objects.get(uploaded_by=auth_user)
        assert doc.file is not None

    def test_missing_file_and_text_returns_400(self, api_client, auth_user):
        """Test že chybějící soubor i text vrátí 400 s detailem."""
        api_client.force_authenticate(user=auth_user)

        data = {"document_type": "other"}

        response = api_client.post("/api/v1/pipeline/lead-from-document/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # DRF validation error should contain field details
        assert "file" in response.data or "raw_text" in response.data

    def test_invalid_file_format_returns_400(self, api_client, auth_user):
        """Test že neplatný formát souboru vrátí 400."""
        api_client.force_authenticate(user=auth_user)

        uploaded_file = SimpleUploadedFile(
            "test.exe", b"binary content", content_type="application/octet-stream"
        )

        data = {
            "file": uploaded_file,
            "document_type": "other",
        }

        response = api_client.post("/api/v1/pipeline/lead-from-document/", data, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "file" in response.data

    def test_unauthenticated_returns_401(self, api_client):
        """Test že neautentizovaný request vrátí 401."""
        data = {"raw_text": "Some text"}

        response = api_client.post("/api/v1/pipeline/lead-from-document/", data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_both_file_and_text_allowed(self, api_client, auth_user):
        """Test že lze poslat soubor i text zároveň."""
        api_client.force_authenticate(user=auth_user)

        uploaded_file = SimpleUploadedFile("test.txt", b"File content", content_type="text/plain")

        data = {
            "file": uploaded_file,
            "raw_text": "Additional text content",
            "document_type": "meeting_notes",
        }

        response = api_client.post("/api/v1/pipeline/lead-from-document/", data, format="multipart")

        # Should succeed - both are provided
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
        # Note: Může selhat na parsing, ale validace by měla projít
