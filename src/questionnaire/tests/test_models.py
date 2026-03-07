import pytest
from django.test import TestCase

from src.accounts.models import User
from src.pipeline.models import Deal
from src.questionnaire.models import QuestionnaireResponse


@pytest.mark.django_db
class TestQuestionnaireModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="vadim", role=User.Role.VADIM)
        self.deal = Deal.objects.create(
            client_company="Test Corp",
            client_contact_name="Jan Novák",
            client_email="jan@test.cz",
            created_by=self.user,
        )

    def test_create_minimal_questionnaire(self):
        q = QuestionnaireResponse.objects.create(
            deal=self.deal,
            filled_by=self.user,
        )
        assert q.pk is not None
        assert str(q) == "Dotazník: Test Corp"

    def test_create_full_section_a(self):
        q = QuestionnaireResponse.objects.create(
            deal=self.deal,
            filled_by=self.user,
            a_company_name="Firma s.r.o.",
            a_ico="12345678",
            a_contact_person="Karel Nový",
            a_email="karel@firma.cz",
            a_phone="+420777123456",
            a_industry="it",
            a_employee_count="small",
            a_annual_revenue="1_10m",
            a_current_it=["crm", "erp", "website"],
            a_it_satisfaction="partial",
        )
        assert q.a_company_name == "Firma s.r.o."
        assert q.a_current_it == ["crm", "erp", "website"]

    def test_array_fields_default_to_empty_list(self):
        q = QuestionnaireResponse.objects.create(
            deal=self.deal,
            filled_by=self.user,
        )
        assert q.b_main_categories == []
        assert q.c_platform == []
        assert q.e_ai_solution_type == []

    def test_conditional_sections_can_be_blank(self):
        q = QuestionnaireResponse.objects.create(
            deal=self.deal,
            filled_by=self.user,
            b_main_categories=["website_eshop"],
            # Section C fields left blank — valid because custom_dev not selected
        )
        assert q.c_platform == []
        assert q.c_key_features == ""

    def test_multiple_categories(self):
        q = QuestionnaireResponse.objects.create(
            deal=self.deal,
            filled_by=self.user,
            b_main_categories=["custom_dev", "ai_automation", "integration"],
        )
        assert len(q.b_main_categories) == 3
        assert "custom_dev" in q.b_main_categories

    def test_date_fields(self):
        from datetime import date

        q = QuestionnaireResponse.objects.create(
            deal=self.deal,
            filled_by=self.user,
            k_specific_deadline=date(2026, 6, 15),
            m_next_contact_date=date(2026, 3, 20),
        )
        assert q.k_specific_deadline == date(2026, 6, 15)
        assert q.m_next_contact_date == date(2026, 3, 20)
