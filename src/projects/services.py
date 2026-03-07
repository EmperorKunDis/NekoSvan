from django.utils import timezone

from src.accounts.models import User
from src.notifications.services import (
    create_notification,
    notify_milestone_approved,
    notify_milestone_ready_for_review,
    notify_qa_issue_found,
)
from src.pipeline.models import Deal

from .models import Milestone, MilestoneTemplate, Project

# Fallback template for categories without specific templates
DEFAULT_TEMPLATE = [
    {"title": "Analýza a plánování", "description": "Analýza požadavků, plán implementace"},
    {"title": "Implementace", "description": "Hlavní fáze vývoje"},
    {"title": "Testování a QA", "description": "Testování, opravy"},
    {"title": "Deploy a předání", "description": "Nasazení a předání klientovi"},
]


def create_project_from_deal(deal: Deal, template_id: int | None = None) -> Project:
    """Create a project with milestone templates based on deal's questionnaire.

    Args:
        deal: The Deal to create project for
        template_id: Optional specific MilestoneTemplate ID to use
    """
    project, created = Project.objects.get_or_create(deal=deal)

    if not created:
        return project

    # Get primary category from questionnaire
    primary_category = None
    if hasattr(deal, "questionnaire"):
        categories = deal.questionnaire.b_main_categories or []
        if categories:
            primary_category = categories[0]

    # Try to find a template
    template = None
    if template_id:
        # Use specified template
        template = MilestoneTemplate.objects.filter(id=template_id, is_active=True).first()
    elif primary_category:
        # Find default template for this category
        template = MilestoneTemplate.objects.filter(
            category=primary_category,
            is_default=True,
            is_active=True,
        ).first()

    if template:
        # Create milestones from database template
        for item in template.items.all():
            Milestone.objects.create(
                project=project,
                title=item.title,
                description=item.description,
                order=item.order,
            )
    else:
        # Use fallback hardcoded template
        for i, tmpl in enumerate(DEFAULT_TEMPLATE):
            Milestone.objects.create(
                project=project,
                title=tmpl["title"],
                description=tmpl["description"],
                order=i + 1,
            )

    return project


def mark_milestone_dev_complete(milestone: Milestone, demo_url: str = "") -> Milestone:
    """Martin marks a milestone as development complete."""
    milestone.status = Milestone.Status.QA_REVIEW
    milestone.dev_completed_at = timezone.now()
    if demo_url:
        milestone.demo_url = demo_url
    milestone.save(update_fields=["status", "dev_completed_at", "demo_url"])

    # Notify NekoSvan QA team
    notify_milestone_ready_for_review(milestone)

    return milestone


def qa_approve_milestone(milestone: Milestone) -> Milestone:
    """NekoSvan approves milestone QA."""
    milestone.status = Milestone.Status.CLIENT_REVIEW
    milestone.qa_approved_at = timezone.now()
    milestone.save(update_fields=["status", "qa_approved_at"])

    # Notify Vadim to present to client
    deal = milestone.project.deal
    for user in User.objects.filter(role=User.Role.VADIM, is_active=True):
        create_notification(
            user=user,
            title=f"Checkpoint: {milestone.title}",
            message=f"Milestone '{milestone.title}' pro {deal.client_company} prošel QA. Prezentujte klientovi.",
            deal=deal,
        )

    return milestone


def qa_reject_milestone(milestone: Milestone, feedback: str) -> Milestone:
    """NekoSvan rejects milestone, back to dev."""
    milestone.status = Milestone.Status.IN_PROGRESS
    milestone.client_feedback = feedback
    milestone.save(update_fields=["status", "client_feedback"])

    # Notify Martin about QA rejection
    deal = milestone.project.deal
    for user in User.objects.filter(role=User.Role.MARTIN, is_active=True):
        create_notification(
            user=user,
            title=f"QA zamítnut: {milestone.title}",
            message=f"Milestone '{milestone.title}' ({deal.client_company}) zamítnut QA: {feedback}",
            deal=deal,
        )

    notify_qa_issue_found(milestone, feedback)

    return milestone


def client_approve_milestone(milestone: Milestone) -> Milestone:
    """Client approves a milestone."""
    milestone.status = Milestone.Status.APPROVED
    milestone.client_approved_at = timezone.now()
    milestone.save(update_fields=["status", "client_approved_at"])

    # Notify Martin that client approved
    deal = milestone.project.deal
    for user in User.objects.filter(role=User.Role.MARTIN, is_active=True):
        create_notification(
            user=user,
            title=f"Klient schválil: {milestone.title}",
            message=f"Milestone '{milestone.title}' ({deal.client_company}) schválen klientem.",
            deal=deal,
        )

    notify_milestone_approved(milestone)

    return milestone


def client_reject_milestone(milestone: Milestone, feedback: str) -> Milestone:
    """Client rejects a milestone, back to dev."""
    milestone.status = Milestone.Status.REJECTED
    milestone.client_feedback = feedback
    milestone.save(update_fields=["status", "client_feedback"])

    # Notify Martin about client rejection
    deal = milestone.project.deal
    for user in User.objects.filter(role=User.Role.MARTIN, is_active=True):
        create_notification(
            user=user,
            title=f"Klient zamítl: {milestone.title}",
            message=f"Milestone '{milestone.title}' ({deal.client_company}) zamítnut klientem: {feedback}",
            deal=deal,
        )

    return milestone
