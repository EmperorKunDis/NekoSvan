import pytest
from django.test import TestCase

from src.accounts.models import User
from src.pipeline.models import Deal
from src.pricing.services import calculate_proposal
from src.questionnaire.models import QuestionnaireResponse


@pytest.mark.django_db
class TestPricingCalculation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="vadim", role=User.Role.VADIM)
        self.deal = Deal.objects.create(
            client_company="Test Corp",
            client_contact_name="Jan Novák",
            client_email="jan@test.cz",
            created_by=self.user,
        )

    def test_basic_website_calculation(self):
        q = QuestionnaireResponse.objects.create(
            deal=self.deal,
            filled_by=self.user,
            b_main_categories=["website_eshop"],
            b_estimated_users="1_5",
        )
        result = calculate_proposal(q)
        assert result["total_price"] > 0
        assert result["deposit_amount"] > 0
        assert len(result["items"]) >= 1

    def test_complex_multi_category_higher_price(self):
        q_simple = QuestionnaireResponse.objects.create(
            deal=self.deal,
            filled_by=self.user,
            b_main_categories=["website_eshop"],
            b_estimated_users="1_5",
        )
        simple_result = calculate_proposal(q_simple)

        deal2 = Deal.objects.create(
            client_company="Big Corp",
            client_contact_name="Petr Velký",
            client_email="petr@big.cz",
            created_by=self.user,
        )
        q_complex = QuestionnaireResponse.objects.create(
            deal=deal2,
            filled_by=self.user,
            b_main_categories=["custom_dev", "ai_automation", "integration"],
            b_estimated_users="201_1000",
            c_platform=["web", "mobile_ios", "mobile_android"],
            c_has_design="no_need",
            g_systems_to_connect=["erp", "crm", "accounting"],
        )
        complex_result = calculate_proposal(q_complex)

        assert complex_result["total_price"] > simple_result["total_price"]

    def test_deposit_is_percentage_of_total(self):
        q = QuestionnaireResponse.objects.create(
            deal=self.deal,
            filled_by=self.user,
            b_main_categories=["ai_automation"],
            b_estimated_users="21_50",
        )
        result = calculate_proposal(q)
        expected_deposit = result["total_price"] * 0.3
        assert abs(result["deposit_amount"] - expected_deposit) < 1
