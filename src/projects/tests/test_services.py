import pytest
from django.test import TestCase

from src.accounts.models import User
from src.pipeline.models import Deal
from src.projects.models import Milestone
from src.projects.services import (
    client_approve_milestone,
    client_reject_milestone,
    create_project_from_deal,
    mark_milestone_dev_complete,
    qa_approve_milestone,
    qa_reject_milestone,
)
from src.questionnaire.models import QuestionnaireResponse


@pytest.mark.django_db
class TestProjectServices(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="martin", role=User.Role.MARTIN)
        self.deal = Deal.objects.create(
            client_company="Test Corp",
            client_contact_name="Jan Novák",
            client_email="jan@test.cz",
            created_by=self.user,
        )

    def test_create_project_with_default_milestones(self):
        project = create_project_from_deal(self.deal)
        assert project.deal == self.deal
        assert project.milestones.count() > 0

    def test_create_project_uses_questionnaire_type(self):
        QuestionnaireResponse.objects.create(
            deal=self.deal,
            b_main_categories=["integration"],
            b_estimated_users="6_20",
            k_budget_range="50_100k",
            filled_by=self.user,
        )
        project = create_project_from_deal(self.deal)
        # Integration template has 4 milestones
        assert project.milestones.count() == 4

    def test_milestone_workflow(self):
        project = create_project_from_deal(self.deal)
        milestone = project.milestones.first()

        # Dev completes
        milestone = mark_milestone_dev_complete(milestone, demo_url="https://demo.test.cz")
        assert milestone.status == Milestone.Status.QA_REVIEW
        assert milestone.dev_completed_at is not None
        assert milestone.demo_url == "https://demo.test.cz"

        # QA approves
        milestone = qa_approve_milestone(milestone)
        assert milestone.status == Milestone.Status.CLIENT_REVIEW
        assert milestone.qa_approved_at is not None

        # Client approves
        milestone = client_approve_milestone(milestone)
        assert milestone.status == Milestone.Status.APPROVED
        assert milestone.client_approved_at is not None

    def test_qa_reject_goes_back_to_dev(self):
        project = create_project_from_deal(self.deal)
        milestone = project.milestones.first()
        milestone = mark_milestone_dev_complete(milestone)
        milestone = qa_reject_milestone(milestone, "Needs fixing")
        assert milestone.status == Milestone.Status.IN_PROGRESS
        assert milestone.client_feedback == "Needs fixing"

    def test_client_reject_milestone(self):
        project = create_project_from_deal(self.deal)
        milestone = project.milestones.first()
        milestone.status = Milestone.Status.CLIENT_REVIEW
        milestone.save()
        milestone = client_reject_milestone(milestone, "Not what we wanted")
        assert milestone.status == Milestone.Status.REJECTED
        assert milestone.client_feedback == "Not what we wanted"

    def test_project_progress(self):
        project = create_project_from_deal(self.deal)
        total = project.milestones.count()
        assert project.progress_percent == 0

        # Approve first milestone
        first = project.milestones.first()
        first.status = Milestone.Status.APPROVED
        first.save()
        project.refresh_from_db()
        expected = int((1 / total) * 100)
        assert project.progress_percent == expected
