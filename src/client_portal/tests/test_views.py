import pytest
from django.test import TestCase
from rest_framework.test import APIClient

from src.accounts.models import User
from src.pipeline.models import Deal
from src.pricing.models import Proposal
from src.projects.models import Milestone
from src.projects.services import create_project_from_deal


@pytest.mark.django_db
class TestClientPortalAPI(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="vadim", role=User.Role.VADIM)
        self.deal = Deal.objects.create(
            client_company="Test Corp",
            client_contact_name="Jan Novák",
            client_email="jan@test.cz",
            phase=Deal.Phase.PRESENTATION,
            created_by=self.user,
        )
        self.token = str(self.deal.portal_token)
        self.client_api = APIClient()

    def test_portal_dashboard_valid_token(self):
        response = self.client_api.get(f"/portal/{self.token}/")
        assert response.status_code == 200
        assert response.data["deal"]["client_company"] == "Test Corp"

    def test_portal_dashboard_invalid_token(self):
        response = self.client_api.get("/portal/00000000-0000-0000-0000-000000000000/")
        assert response.status_code == 404

    def test_portal_shows_proposal(self):
        Proposal.objects.create(
            deal=self.deal, version=1, total_price=100000,
            deposit_amount=30000, status="sent", created_by=self.user,
        )
        response = self.client_api.get(f"/portal/{self.token}/")
        assert response.data["proposal"] is not None
        assert response.data["proposal"]["total_price"] == "100000.00"

    def test_portal_accept_proposal(self):
        Proposal.objects.create(
            deal=self.deal, version=1, total_price=100000,
            deposit_amount=30000, status="sent", created_by=self.user,
        )
        # Need adam for auto-assignment
        User.objects.create_user(username="adam", role=User.Role.ADAM)

        response = self.client_api.post(f"/portal/{self.token}/proposal/accept/")
        assert response.status_code == 200
        assert response.data["status"] == "accepted"

        self.deal.refresh_from_db()
        assert self.deal.phase == Deal.Phase.CONTRACT

    def test_portal_reject_proposal(self):
        User.objects.create_user(username="martin", role=User.Role.MARTIN)
        Proposal.objects.create(
            deal=self.deal, version=1, total_price=100000,
            deposit_amount=30000, status="sent", created_by=self.user,
        )
        response = self.client_api.post(
            f"/portal/{self.token}/proposal/reject/",
            {"feedback": "Too expensive"},
            format="json",
        )
        assert response.status_code == 200
        self.deal.refresh_from_db()
        assert self.deal.phase == Deal.Phase.PRICING
        assert self.deal.revision_count == 1

    def test_portal_milestone_approve(self):
        self.deal.phase = Deal.Phase.DEVELOPMENT
        self.deal.save()
        project = create_project_from_deal(self.deal)
        milestone = project.milestones.first()
        milestone.status = Milestone.Status.CLIENT_REVIEW
        milestone.save()

        response = self.client_api.post(
            f"/portal/{self.token}/milestone/{milestone.id}/approve/"
        )
        assert response.status_code == 200
        milestone.refresh_from_db()
        assert milestone.status == Milestone.Status.APPROVED

    def test_portal_milestone_reject(self):
        self.deal.phase = Deal.Phase.DEVELOPMENT
        self.deal.save()
        project = create_project_from_deal(self.deal)
        milestone = project.milestones.first()
        milestone.status = Milestone.Status.CLIENT_REVIEW
        milestone.save()

        response = self.client_api.post(
            f"/portal/{self.token}/milestone/{milestone.id}/reject/",
            {"feedback": "Needs changes"},
            format="json",
        )
        assert response.status_code == 200
        milestone.refresh_from_db()
        assert milestone.status == Milestone.Status.REJECTED
        assert milestone.client_feedback == "Needs changes"

    def test_portal_milestone_reject_wrong_status(self):
        self.deal.phase = Deal.Phase.DEVELOPMENT
        self.deal.save()
        project = create_project_from_deal(self.deal)
        milestone = project.milestones.first()
        # Milestone is still PENDING, not in CLIENT_REVIEW

        response = self.client_api.post(
            f"/portal/{self.token}/milestone/{milestone.id}/approve/"
        )
        assert response.status_code == 404
