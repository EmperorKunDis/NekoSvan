import pytest
from django.test import TestCase

from src.accounts.models import User
from src.pipeline.models import Deal
from src.questionnaire.serializers import (
    AIExtractSerializer,
    QuestionnaireResponseSerializer,
)


@pytest.mark.django_db
class TestQuestionnaireSerializer(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="vadim", role=User.Role.VADIM)
        self.deal = Deal.objects.create(
            client_company="Test Corp",
            client_contact_name="Jan Novák",
            client_email="jan@test.cz",
            created_by=self.user,
        )

    def test_valid_minimal_data(self):
        data = {"deal": self.deal.pk}
        s = QuestionnaireResponseSerializer(data=data)
        assert s.is_valid(), s.errors

    def test_valid_array_field_values(self):
        data = {
            "deal": self.deal.pk,
            "a_current_it": ["crm", "erp"],
            "b_main_categories": ["custom_dev", "ai_automation"],
        }
        s = QuestionnaireResponseSerializer(data=data)
        assert s.is_valid(), s.errors

    def test_invalid_array_field_values(self):
        data = {
            "deal": self.deal.pk,
            "a_current_it": ["crm", "INVALID_VALUE"],
        }
        s = QuestionnaireResponseSerializer(data=data)
        assert not s.is_valid()
        assert "a_current_it" in s.errors

    def test_invalid_main_categories(self):
        data = {
            "deal": self.deal.pk,
            "b_main_categories": ["custom_dev", "nonexistent"],
        }
        s = QuestionnaireResponseSerializer(data=data)
        assert not s.is_valid()
        assert "b_main_categories" in s.errors

    def test_all_sections_valid(self):
        data = {
            "deal": self.deal.pk,
            "a_company_name": "Firma",
            "a_industry": "it",
            "b_main_categories": ["custom_dev"],
            "b_primary_goal": "new_product",
            "c_platform": ["web", "mobile_ios"],
            "k_budget_range": "250_500k",
            "m_lead_rating": "warm",
        }
        s = QuestionnaireResponseSerializer(data=data)
        assert s.is_valid(), s.errors


class TestAIExtractSerializer(TestCase):
    def test_valid_text(self):
        s = AIExtractSerializer(data={"text": "Some client description"})
        assert s.is_valid()

    def test_empty_both_fields(self):
        s = AIExtractSerializer(data={})
        assert not s.is_valid()

    def test_empty_text_no_file(self):
        s = AIExtractSerializer(data={"text": ""})
        assert not s.is_valid()
