"""E2E test: deal passes through all 8 phases with notifications, payments, and project creation."""

import pytest
from django.utils import timezone

from src.accounts.models import Company, User
from src.contracts.models import Contract, ContractTemplate, Payment
from src.notifications.models import Notification
from src.pipeline import services as pipeline_services
from src.pipeline.models import Deal, DealActivity
from src.pricing.models import Proposal
from src.projects import services as project_services
from src.projects.models import Milestone, Project
from src.questionnaire.models import QuestionnaireResponse


@pytest.fixture()
def company():
    return Company.objects.create(name=Company.CompanyName.ADNP, ico="12345678")


@pytest.fixture()
def adam(company):
    return User.objects.create_user(
        username="adam", email="adam@adnp.cz", password="test",
        role=User.Role.ADAM, company=company,
    )


@pytest.fixture()
def vadim():
    return User.objects.create_user(
        username="vadim", email="vadim@example.com", password="test",
        role=User.Role.VADIM,
    )


@pytest.fixture()
def martin():
    return User.objects.create_user(
        username="martin", email="martin@praut.cz", password="test",
        role=User.Role.MARTIN,
    )


@pytest.fixture()
def nekosvan():
    return User.objects.create_user(
        username="nekosvan", email="info@nekosvan.cz", password="test",
        role=User.Role.NEKOSVAN,
    )


@pytest.fixture()
def contract_template():
    return ContractTemplate.objects.create(
        name="Test template",
        body_template="Smlouva pro {{client_name}}, cena {{total_price}} Kč.",
    )


@pytest.mark.django_db()
def test_full_8_phase_workflow(adam, vadim, martin, nekosvan, contract_template):
    """Test complete deal lifecycle: lead → completed."""

    # === PHASE 1: LEAD → QUALIFICATION (Adam creates deal) ===
    deal = Deal.objects.create(
        client_company="TestCorp s.r.o.",
        client_contact_name="Jan Novák",
        client_email="jan@testcorp.cz",
        client_phone="+420123456789",
        created_by=adam,
    )
    deal = pipeline_services.advance_phase(deal, adam, note="New lead created")

    assert deal.phase == Deal.Phase.QUALIFICATION
    assert deal.assigned_to == vadim
    # Notification sent to Vadim
    assert Notification.objects.filter(user=vadim, deal=deal).exists()

    # === PHASE 2: QUALIFICATION → PRICING (Vadim fills questionnaire) ===
    QuestionnaireResponse.objects.create(
        deal=deal,
        b_main_categories=["custom_dev"],
        b_primary_goal="new_product",
        b_estimated_users="21_50",
        k_budget_range="100_250k",
        k_launch_deadline="3months",
        c_has_design="no_need",
        filled_by=vadim,
    )
    deal = pipeline_services.advance_phase(deal, vadim, note="Questionnaire filled")

    assert deal.phase == Deal.Phase.PRICING
    assert deal.assigned_to == martin
    assert Notification.objects.filter(user=martin, deal=deal).count() >= 1

    # === PHASE 3: PRICING → PRESENTATION (Martin creates proposal) ===
    proposal = Proposal.objects.create(
        deal=deal,
        version=1,
        base_price=150000,
        items=[
            {"name": "Core funkce", "hours": 60, "rate": 1500, "total": 90000},
            {"name": "UI/UX", "hours": 40, "rate": 1500, "total": 60000},
        ],
        total_price=150000,
        deposit_amount=45000,
        status="sent",
        created_by=martin,
    )
    deal = pipeline_services.advance_phase(deal, martin, note="Proposal sent")

    assert deal.phase == Deal.Phase.PRESENTATION
    assert deal.assigned_to == vadim

    # === PHASE 4: PRESENTATION → CONTRACT (Client accepts via portal) ===
    proposal.status = "accepted"
    proposal.save(update_fields=["status"])

    deal = pipeline_services.advance_phase(deal, vadim, note="Client accepted proposal")

    assert deal.phase == Deal.Phase.CONTRACT
    assert deal.assigned_to == adam

    # === PHASE 5: CONTRACT → PLANNING (Adam generates & signs contract) ===
    Contract.objects.create(
        deal=deal,
        template_used=contract_template,
        status=Contract.Status.SIGNED,
        signed_at=timezone.now(),
        signed_by_client=True,
    )
    # Auto-create payments (simulating mark_signed logic)
    Payment.objects.create(
        deal=deal,
        type=Payment.PaymentType.DEPOSIT,
        amount=proposal.deposit_amount,
        due_date=timezone.now().date(),
        invoice_number=f"INV-{deal.id:04d}-DEP",
    )
    Payment.objects.create(
        deal=deal,
        type=Payment.PaymentType.FINAL,
        amount=proposal.total_price - proposal.deposit_amount,
        due_date=timezone.now().date(),
        invoice_number=f"INV-{deal.id:04d}-FIN",
    )

    # Deposit paid → advance to planning
    deposit = deal.payments.get(type=Payment.PaymentType.DEPOSIT)
    deposit.status = Payment.Status.PAID
    deposit.paid_at = timezone.now()
    deposit.save()

    deal = pipeline_services.advance_phase(deal, adam, note="Deposit received, contract signed")

    assert deal.phase == Deal.Phase.PLANNING
    assert deal.assigned_to == martin
    # Project should be auto-created
    assert Project.objects.filter(deal=deal).exists()
    project = deal.project
    assert project.milestones.count() > 0  # Webapp template milestones

    # === PHASE 6: PLANNING → DEVELOPMENT (Martin confirms plan) ===
    deal = pipeline_services.advance_phase(deal, martin, note="Implementation plan ready")

    assert deal.phase == Deal.Phase.DEVELOPMENT
    assert deal.assigned_to == martin

    # === PHASE 7: DEVELOPMENT — Milestone workflow ===
    milestone = project.milestones.first()
    assert milestone is not None

    # Martin completes milestone
    milestone = project_services.mark_milestone_dev_complete(milestone, demo_url="https://staging.test/demo")
    assert milestone.status == Milestone.Status.QA_REVIEW
    # NekoSvan got notified
    assert Notification.objects.filter(user=nekosvan, title__contains="QA Review").exists()

    # NekoSvan approves QA
    milestone = project_services.qa_approve_milestone(milestone)
    assert milestone.status == Milestone.Status.CLIENT_REVIEW
    # Vadim got notified to present to client
    assert Notification.objects.filter(user=vadim, title__contains="Checkpoint").exists()

    # Client approves milestone
    milestone = project_services.client_approve_milestone(milestone)
    assert milestone.status == Milestone.Status.APPROVED
    # Martin got notified
    assert Notification.objects.filter(user=martin, title__contains="schválil").exists()

    # === PHASE 8: DEVELOPMENT → COMPLETED ===
    deal = pipeline_services.advance_phase(deal, nekosvan, note="All milestones complete, final QA passed")

    assert deal.phase == Deal.Phase.COMPLETED
    assert deal.status == Deal.Status.ACTIVE

    # === VERIFY FINAL STATE ===
    # All 8 phase transitions logged
    activities = DealActivity.objects.filter(deal=deal, action__startswith="phase_changed")
    assert activities.count() == 7  # 7 transitions for 8 phases

    # Payments exist
    assert deal.payments.count() == 2

    # Contract exists and is signed
    assert deal.contract.status == Contract.Status.SIGNED

    # Project has milestones
    assert deal.project.milestones.count() > 0

    # Notifications were created throughout
    total_notifications = Notification.objects.filter(deal=deal).count()
    assert total_notifications >= 7  # At least one per phase change


@pytest.mark.django_db()
def test_revision_flow(adam, vadim, martin, nekosvan):
    """Test deal revision: presentation → pricing → presentation → contract."""
    deal = Deal.objects.create(
        client_company="RevisionCorp",
        client_contact_name="Petr Dvořák",
        client_email="petr@revision.cz",
        created_by=adam,
    )

    # Advance to presentation
    deal = pipeline_services.advance_phase(deal, adam)
    deal = pipeline_services.advance_phase(deal, vadim)
    deal = pipeline_services.advance_phase(deal, martin)
    assert deal.phase == Deal.Phase.PRESENTATION

    # Client rejects → back to pricing
    deal = pipeline_services.request_revision(deal, vadim, "Price too high")
    assert deal.phase == Deal.Phase.PRICING
    assert deal.revision_count == 1
    assert deal.assigned_to == martin

    # Martin adjusts, sends again
    deal = pipeline_services.advance_phase(deal, martin)
    assert deal.phase == Deal.Phase.PRESENTATION

    # Client accepts this time
    deal = pipeline_services.advance_phase(deal, vadim)
    assert deal.phase == Deal.Phase.CONTRACT


@pytest.mark.django_db()
def test_max_revisions_archives(adam, vadim, martin, nekosvan):
    """Test that 3 revisions archive the deal."""
    deal = Deal.objects.create(
        client_company="ArchiveCorp",
        client_contact_name="Karel",
        client_email="k@archive.cz",
        created_by=adam,
    )

    # Advance to presentation
    deal = pipeline_services.advance_phase(deal, adam)
    deal = pipeline_services.advance_phase(deal, vadim)
    deal = pipeline_services.advance_phase(deal, martin)

    # 3 rejections
    for i in range(3):
        deal = pipeline_services.request_revision(deal, vadim, f"Revision {i+1}")
        if deal.status == Deal.Status.ARCHIVED:
            break
        deal = pipeline_services.advance_phase(deal, martin)

    assert deal.status == Deal.Status.ARCHIVED
    assert deal.revision_count == 3
