import pytest
from django.test import TestCase
from rest_framework.test import APIClient

from src.accounts.models import User
from src.pipeline.models import Deal


@pytest.mark.django_db
class TestDealAPI(TestCase):
    def setUp(self):
        self.adam = User.objects.create_user(
            username="adam", password="testpass123", role=User.Role.ADAM,
            first_name="Adam", last_name="Test",
        )
        self.vadim = User.objects.create_user(
            username="vadim", password="testpass123", role=User.Role.VADIM,
            first_name="Vadim", last_name="Test",
        )
        self.martin = User.objects.create_user(
            username="martin", password="testpass123", role=User.Role.MARTIN,
            first_name="Martin", last_name="Test",
        )
        self.client_api = APIClient()
        self.client_api.force_authenticate(user=self.adam)

    def test_create_deal_auto_advances_to_qualification(self):
        response = self.client_api.post("/api/v1/pipeline/deals/", {
            "client_company": "Test Corp",
            "client_contact_name": "Jan Novák",
            "client_email": "jan@test.cz",
        })
        assert response.status_code == 201
        deal = Deal.objects.get(id=response.data["id"])
        assert deal.phase == Deal.Phase.QUALIFICATION
        assert deal.assigned_to == self.vadim

    def test_advance_deal(self):
        deal = Deal.objects.create(
            client_company="Test Corp",
            client_contact_name="Jan Novák",
            client_email="jan@test.cz",
            phase=Deal.Phase.QUALIFICATION,
            assigned_to=self.vadim,
            created_by=self.adam,
        )
        # Vadim advances from qualification
        vadim_client = APIClient()
        vadim_client.force_authenticate(user=self.vadim)
        response = vadim_client.post(
            f"/api/v1/pipeline/deals/{deal.id}/advance/",
            {"note": "Questionnaire done"},
        )
        assert response.status_code == 200
        assert response.data["phase"] == Deal.Phase.PRICING

    def test_request_revision(self):
        deal = Deal.objects.create(
            client_company="Test Corp",
            client_contact_name="Jan Novák",
            client_email="jan@test.cz",
            phase=Deal.Phase.PRESENTATION,
            assigned_to=self.vadim,
            created_by=self.adam,
        )
        # Vadim requests revision from presentation
        vadim_client = APIClient()
        vadim_client.force_authenticate(user=self.vadim)
        response = vadim_client.post(
            f"/api/v1/pipeline/deals/{deal.id}/revision/",
            {"feedback": "Too expensive"},
        )
        assert response.status_code == 200
        assert response.data["phase"] == Deal.Phase.PRICING
        assert response.data["revision_count"] == 1

    def test_deal_timeline(self):
        deal = Deal.objects.create(
            client_company="Test Corp",
            client_contact_name="Jan Novák",
            client_email="jan@test.cz",
            phase=Deal.Phase.LEAD,
            created_by=self.adam,
        )
        # Advance to create activity
        self.client_api.post(f"/api/v1/pipeline/deals/{deal.id}/advance/")
        response = self.client_api.get(f"/api/v1/pipeline/deals/{deal.id}/timeline/")
        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_list_deals_filter_by_phase(self):
        Deal.objects.create(
            client_company="A", client_contact_name="A", client_email="a@a.cz",
            phase=Deal.Phase.LEAD, created_by=self.adam,
        )
        Deal.objects.create(
            client_company="B", client_contact_name="B", client_email="b@b.cz",
            phase=Deal.Phase.PRICING, created_by=self.adam,
        )
        response = self.client_api.get("/api/v1/pipeline/deals/?phase=lead")
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_unauthenticated_access_denied(self):
        client = APIClient()
        response = client.get("/api/v1/pipeline/deals/")
        assert response.status_code == 403


@pytest.mark.django_db
class TestDashboardAPI(TestCase):
    def setUp(self):
        self.adam = User.objects.create_user(
            username="adam", password="testpass123", role=User.Role.ADAM,
            first_name="Adam", last_name="Test",
        )
        self.vadim = User.objects.create_user(
            username="vadim", password="testpass123", role=User.Role.VADIM,
            first_name="Vadim", last_name="Test",
        )
        self.martin = User.objects.create_user(
            username="martin", password="testpass123", role=User.Role.MARTIN,
            first_name="Martin", last_name="Test",
        )
        self.nekosvan = User.objects.create_user(
            username="nekosvan", password="testpass123", role=User.Role.NEKOSVAN,
            first_name="Neko", last_name="Svan",
        )

    def test_adam_dashboard(self):
        client = APIClient()
        client.force_authenticate(user=self.adam)
        response = client.get("/api/v1/pipeline/dashboard/")
        assert response.status_code == 200
        assert response.data["role"] == "adam"
        assert "pipeline_overview" in response.data

    def test_vadim_dashboard(self):
        client = APIClient()
        client.force_authenticate(user=self.vadim)
        response = client.get("/api/v1/pipeline/dashboard/")
        assert response.status_code == 200
        assert response.data["role"] == "vadim"
        assert "leads_to_call" in response.data

    def test_martin_dashboard(self):
        client = APIClient()
        client.force_authenticate(user=self.martin)
        response = client.get("/api/v1/pipeline/dashboard/")
        assert response.status_code == 200
        assert response.data["role"] == "martin"
        assert "deals_to_price" in response.data

    def test_nekosvan_dashboard(self):
        client = APIClient()
        client.force_authenticate(user=self.nekosvan)
        response = client.get("/api/v1/pipeline/dashboard/")
        assert response.status_code == 200
        assert response.data["role"] == "nekosvan"
        assert "qa_review_queue" in response.data
        assert "stats" in response.data
