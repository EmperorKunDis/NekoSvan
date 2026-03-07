from unittest.mock import patch

import pytest
from django.test import TestCase
from rest_framework.test import APIClient

from src.accounts.models import User
from src.pipeline.models import Deal
from src.questionnaire.models import QuestionnaireResponse


@pytest.mark.django_db
class TestQuestionnaireViewSet(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="vadim", password="testpass", role=User.Role.VADIM
        )
        self.deal = Deal.objects.create(
            client_company="Test Corp",
            client_contact_name="Jan Novák",
            client_email="jan@test.cz",
            phase=Deal.Phase.QUALIFICATION,
            created_by=self.user,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_questionnaire(self):
        resp = self.client.post(
            "/api/v1/questionnaire/questionnaires/",
            {
                "deal": self.deal.pk,
                "b_main_categories": ["custom_dev"],
                "k_budget_range": "100_250k",
            },
            format="json",
        )
        assert resp.status_code == 201
        assert QuestionnaireResponse.objects.filter(deal=self.deal).exists()

    def test_create_auto_advances_deal(self):
        self.client.post(
            "/api/v1/questionnaire/questionnaires/",
            {"deal": self.deal.pk},
            format="json",
        )
        self.deal.refresh_from_db()
        assert self.deal.phase == Deal.Phase.PRICING

    def test_duplicate_questionnaire_rejected(self):
        QuestionnaireResponse.objects.create(
            deal=self.deal, filled_by=self.user
        )
        resp = self.client.post(
            "/api/v1/questionnaire/questionnaires/",
            {"deal": self.deal.pk},
            format="json",
        )
        assert resp.status_code == 400

    def test_sync_to_deal_on_create(self):
        self.client.post(
            "/api/v1/questionnaire/questionnaires/",
            {
                "deal": self.deal.pk,
                "a_company_name": "Nová Firma",
                "a_contact_person": "Karel Nový",
                "a_email": "karel@nova.cz",
                "a_phone": "+420777111222",
                "a_ico": "99887766",
            },
            format="json",
        )
        self.deal.refresh_from_db()
        assert self.deal.client_company == "Nová Firma"
        assert self.deal.client_contact_name == "Karel Nový"
        assert self.deal.client_email == "karel@nova.cz"
        assert self.deal.client_ico == "99887766"

    def test_ai_extract_no_data(self):
        resp = self.client.post(
            "/api/v1/questionnaire/questionnaires/ai-extract/",
            {},
            format="json",
        )
        assert resp.status_code == 400

    @patch("src.questionnaire.views.extract_from_text")
    def test_ai_extract_success(self, mock_extract):
        mock_extract.return_value = {
            "a_company_name": "AI Corp",
            "b_main_categories": ["ai_automation"],
        }
        resp = self.client.post(
            "/api/v1/questionnaire/questionnaires/ai-extract/",
            {"text": "Company AI Corp wants AI automation project"},
            format="json",
        )
        assert resp.status_code == 200
        assert resp.json()["extracted"]["a_company_name"] == "AI Corp"

    @patch("src.questionnaire.views.extract_from_text")
    def test_ai_extract_ollama_down(self, mock_extract):
        from src.questionnaire.services import OllamaUnavailableError

        mock_extract.side_effect = OllamaUnavailableError("Cannot connect")
        resp = self.client.post(
            "/api/v1/questionnaire/questionnaires/ai-extract/",
            {"text": "Some text"},
            format="json",
        )
        assert resp.status_code == 503
