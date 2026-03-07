import pytest
from django.test import TestCase

from src.accounts.models import Company, User
from src.pipeline.models import Deal, DealActivity
from src.pipeline.services import advance_phase, request_revision


@pytest.mark.django_db
class TestPhaseTransitions(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="adnp", legal_name="ADNP s.r.o.")
        self.adam = User.objects.create_user(
            username="adam", role=User.Role.ADAM, company=self.company,
            first_name="Adam", last_name="Test",
        )
        self.vadim = User.objects.create_user(
            username="vadim", role=User.Role.VADIM,
            first_name="Vadim", last_name="Test",
        )
        self.martin = User.objects.create_user(
            username="martin", role=User.Role.MARTIN,
            first_name="Martin", last_name="Test",
        )
        self.nekosvan = User.objects.create_user(
            username="nekosvan", role=User.Role.NEKOSVAN,
            first_name="Neko", last_name="Svan",
        )
        self.deal = Deal.objects.create(
            client_company="Test Corp",
            client_contact_name="Jan Novák",
            client_email="jan@test.cz",
            phase=Deal.Phase.LEAD,
            created_by=self.adam,
        )

    def test_advance_from_lead_assigns_vadim(self):
        deal = advance_phase(self.deal, self.adam, note="New lead")
        assert deal.phase == Deal.Phase.QUALIFICATION
        assert deal.assigned_to == self.vadim

    def test_advance_through_all_phases(self):
        phases = [
            (Deal.Phase.QUALIFICATION, self.vadim),
            (Deal.Phase.PRICING, self.martin),
            (Deal.Phase.PRESENTATION, self.vadim),
            (Deal.Phase.CONTRACT, self.adam),
            (Deal.Phase.PLANNING, self.martin),
            (Deal.Phase.DEVELOPMENT, self.martin),
            (Deal.Phase.COMPLETED, self.nekosvan),
        ]
        deal = self.deal
        for expected_phase, expected_assignee in phases:
            deal = advance_phase(deal, self.adam)
            assert deal.phase == expected_phase
            assert deal.assigned_to == expected_assignee

    def test_cannot_advance_from_completed(self):
        self.deal.phase = Deal.Phase.COMPLETED
        self.deal.save()
        with pytest.raises(ValueError, match="Cannot advance"):
            advance_phase(self.deal, self.adam)

    def test_activity_logged_on_advance(self):
        advance_phase(self.deal, self.adam)
        activity = DealActivity.objects.filter(deal=self.deal).first()
        assert activity is not None
        assert "phase_changed" in activity.action

    def test_revision_from_presentation(self):
        self.deal.phase = Deal.Phase.PRESENTATION
        self.deal.save()
        deal = request_revision(self.deal, self.vadim, "Needs lower price")
        assert deal.phase == Deal.Phase.PRICING
        assert deal.assigned_to == self.martin
        assert deal.revision_count == 1

    def test_max_revisions_archives_deal(self):
        self.deal.phase = Deal.Phase.PRESENTATION
        self.deal.revision_count = 2
        self.deal.save()
        deal = request_revision(self.deal, self.vadim, "Too expensive again")
        assert deal.status == Deal.Status.ARCHIVED
        assert deal.revision_count == 3
