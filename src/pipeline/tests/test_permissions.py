"""Tests for permissions — all internal users have full access."""

import pytest
from django.test import TestCase
from rest_framework.test import APIClient

from src.accounts.models import User
from src.pipeline.models import Deal


def make_users():
    """Create one user per role."""
    return {
        "adam": User.objects.create_user(
            username="adam", password="test", role=User.Role.ADAM,
            first_name="Adam", last_name="T",
        ),
        "vadim": User.objects.create_user(
            username="vadim", password="test", role=User.Role.VADIM,
            first_name="Vadim", last_name="T",
        ),
        "martin": User.objects.create_user(
            username="martin", password="test", role=User.Role.MARTIN,
            first_name="Martin", last_name="T",
        ),
        "nekosvan": User.objects.create_user(
            username="nekosvan", password="test", role=User.Role.NEKOSVAN,
            first_name="Neko", last_name="Svan",
        ),
        "client": User.objects.create_user(
            username="client", password="test", role=User.Role.CLIENT,
            first_name="Klient", last_name="T",
        ),
    }


def make_deals(creator):
    """Create one deal per phase for testing."""
    deals = {}
    for phase in Deal.Phase.values:
        deals[phase] = Deal.objects.create(
            client_company=f"Test {phase}",
            client_contact_name="Test",
            client_email="t@t.cz",
            phase=phase,
            created_by=creator,
        )
    return deals


@pytest.mark.django_db
class TestAllInternalUsersCanListDeals(TestCase):
    """All internal users see all deals regardless of phase."""

    def setUp(self):
        self.users = make_users()
        self.deals = make_deals(self.users["adam"])

    def _list_deals(self, user):
        c = APIClient()
        c.force_authenticate(user=user)
        resp = c.get("/api/v1/pipeline/deals/")
        assert resp.status_code == 200
        return {d["phase"] for d in resp.data["results"]}

    def test_adam_sees_all(self):
        phases = self._list_deals(self.users["adam"])
        assert len(phases) == len(Deal.Phase.values)

    def test_vadim_sees_all(self):
        phases = self._list_deals(self.users["vadim"])
        assert len(phases) == len(Deal.Phase.values)

    def test_martin_sees_all(self):
        phases = self._list_deals(self.users["martin"])
        assert len(phases) == len(Deal.Phase.values)

    def test_nekosvan_sees_all(self):
        phases = self._list_deals(self.users["nekosvan"])
        assert len(phases) == len(Deal.Phase.values)

    def test_client_role_denied(self):
        c = APIClient()
        c.force_authenticate(user=self.users["client"])
        resp = c.get("/api/v1/pipeline/deals/")
        assert resp.status_code == 403


@pytest.mark.django_db
class TestAllInternalUsersCanAdvance(TestCase):
    """Any internal user can advance any deal."""

    def setUp(self):
        self.users = make_users()

    def test_adam_can_advance_qualification_deal(self):
        deal = Deal.objects.create(
            client_company="X", client_contact_name="X", client_email="x@x.cz",
            phase=Deal.Phase.QUALIFICATION, created_by=self.users["adam"],
            assigned_to=self.users["vadim"],
        )
        c = APIClient()
        c.force_authenticate(user=self.users["adam"])
        resp = c.post(f"/api/v1/pipeline/deals/{deal.id}/advance/", {"note": "x"})
        assert resp.status_code == 200

    def test_vadim_can_advance_qualification_deal(self):
        deal = Deal.objects.create(
            client_company="X", client_contact_name="X", client_email="x@x.cz",
            phase=Deal.Phase.QUALIFICATION, created_by=self.users["adam"],
            assigned_to=self.users["vadim"],
        )
        c = APIClient()
        c.force_authenticate(user=self.users["vadim"])
        resp = c.post(f"/api/v1/pipeline/deals/{deal.id}/advance/", {"note": "done"})
        assert resp.status_code == 200


@pytest.mark.django_db
class TestProposalPermissions(TestCase):
    """Any internal user can create proposals."""

    def setUp(self):
        self.users = make_users()
        self.deal = Deal.objects.create(
            client_company="X", client_contact_name="X", client_email="x@x.cz",
            phase=Deal.Phase.PRICING, created_by=self.users["adam"],
        )

    def test_martin_can_create_proposal(self):
        c = APIClient()
        c.force_authenticate(user=self.users["martin"])
        resp = c.post("/api/v1/pricing/proposals/", {
            "deal": self.deal.id,
            "total_price": "50000",
            "deposit_amount": "15000",
        })
        assert resp.status_code == 201

    def test_adam_can_create_proposal(self):
        c = APIClient()
        c.force_authenticate(user=self.users["adam"])
        resp = c.post("/api/v1/pricing/proposals/", {
            "deal": self.deal.id,
            "total_price": "50000",
            "deposit_amount": "15000",
        })
        assert resp.status_code == 201

    def test_client_denied(self):
        c = APIClient()
        c.force_authenticate(user=self.users["client"])
        resp = c.get("/api/v1/pricing/proposals/")
        assert resp.status_code == 403


@pytest.mark.django_db
class TestContractPermissions(TestCase):
    """Any internal user can write contracts."""

    def setUp(self):
        self.users = make_users()

    def test_martin_can_create_contract(self):
        deal = Deal.objects.create(
            client_company="X", client_contact_name="X", client_email="x@x.cz",
            phase=Deal.Phase.CONTRACT, created_by=self.users["adam"],
        )
        c = APIClient()
        c.force_authenticate(user=self.users["martin"])
        resp = c.post("/api/v1/contracts/contracts/", {"deal": deal.id})
        assert resp.status_code == 201

    def test_adam_can_read_contracts(self):
        c = APIClient()
        c.force_authenticate(user=self.users["adam"])
        resp = c.get("/api/v1/contracts/contracts/")
        assert resp.status_code == 200


@pytest.mark.django_db
class TestPaymentPermissions(TestCase):
    """Any internal user can manage payments."""

    def setUp(self):
        self.users = make_users()

    def test_vadim_can_create_payment(self):
        deal = Deal.objects.create(
            client_company="X", client_contact_name="X", client_email="x@x.cz",
            phase=Deal.Phase.CONTRACT, created_by=self.users["adam"],
        )
        c = APIClient()
        c.force_authenticate(user=self.users["vadim"])
        resp = c.post("/api/v1/contracts/payments/", {
            "deal": deal.id, "type": "deposit", "amount": "10000", "due_date": "2026-04-01",
        })
        assert resp.status_code == 201

    def test_martin_can_read_payments(self):
        c = APIClient()
        c.force_authenticate(user=self.users["martin"])
        resp = c.get("/api/v1/contracts/payments/")
        assert resp.status_code == 200


@pytest.mark.django_db
class TestQuestionnairePermissions(TestCase):
    """Only internal users can access questionnaires."""

    def setUp(self):
        self.users = make_users()

    def test_client_denied(self):
        c = APIClient()
        c.force_authenticate(user=self.users["client"])
        resp = c.get("/api/v1/questionnaire/questionnaires/")
        assert resp.status_code == 403

    def test_vadim_can_read(self):
        c = APIClient()
        c.force_authenticate(user=self.users["vadim"])
        resp = c.get("/api/v1/questionnaire/questionnaires/")
        assert resp.status_code == 200


@pytest.mark.django_db
class TestProjectPermissions(TestCase):
    """Only internal users can access projects."""

    def setUp(self):
        self.users = make_users()

    def test_client_denied(self):
        c = APIClient()
        c.force_authenticate(user=self.users["client"])
        resp = c.get("/api/v1/projects/projects/")
        assert resp.status_code == 403

    def test_martin_can_read(self):
        c = APIClient()
        c.force_authenticate(user=self.users["martin"])
        resp = c.get("/api/v1/projects/projects/")
        assert resp.status_code == 200
