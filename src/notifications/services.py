import logging

import requests
from django.conf import settings

from src.accounts.models import User
from src.pipeline.models import Deal

from .models import Notification

logger = logging.getLogger(__name__)


def create_notification(user: User, title: str, message: str, deal: Deal | None = None, link: str = "") -> Notification:
    """Create an in-app notification."""
    return Notification.objects.create(
        user=user,
        deal=deal,
        title=title,
        message=message,
        link=link,
    )


def trigger_n8n_webhook(event: str, payload: dict) -> bool:
    """Send event to N8N webhook for external notifications (email, etc.)."""
    base_url = getattr(settings, "N8N_WEBHOOK_BASE_URL", "")
    if not base_url:
        logger.warning(f"N8N_WEBHOOK_BASE_URL not configured, skipping event: {event}")
        return False

    url = f"{base_url}/{event}"
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.RequestException:
        logger.exception(f"Failed to trigger N8N webhook: {event}")
        return False


def notify_phase_change(deal: Deal) -> None:
    """Notify relevant users about a deal phase change."""
    if deal.assigned_to:
        create_notification(
            user=deal.assigned_to,
            title=f"Deal přiřazen: {deal.client_company}",
            message=f"Deal {deal.client_company} je ve fázi {deal.get_phase_display()}. Čeká na vaši akci.",
            deal=deal,
        )

    trigger_n8n_webhook("deal.phase_changed", {
        "deal_id": deal.id,
        "client_company": deal.client_company,
        "phase": deal.phase,
        "assigned_to_email": deal.assigned_to.email if deal.assigned_to else "",
        "assigned_to_name": deal.assigned_to.get_full_name() if deal.assigned_to else "",
    })


def notify_milestone_ready_for_review(milestone) -> None:
    """Notify QA team about a milestone ready for review."""
    deal = milestone.project.deal

    # Notify NekoSvan users
    for user in User.objects.filter(role=User.Role.NEKOSVAN, is_active=True):
        create_notification(
            user=user,
            title=f"QA Review: {milestone.title}",
            message=f"Milestone '{milestone.title}' pro {deal.client_company} je připraven na QA review.",
            deal=deal,
        )

    trigger_n8n_webhook("milestone.ready_for_review", {
        "deal_id": deal.id,
        "milestone_id": milestone.id,
        "milestone_title": milestone.title,
        "client_company": deal.client_company,
        "demo_url": milestone.demo_url,
    })


def notify_payment_overdue(payment) -> None:
    """Notify about overdue payment."""
    trigger_n8n_webhook("payment.overdue", {
        "deal_id": payment.deal.id,
        "client_company": payment.deal.client_company,
        "client_email": payment.deal.client_email,
        "amount": str(payment.amount),
        "due_date": str(payment.due_date),
        "invoice_number": payment.invoice_number,
    })


def notify_deal_created(deal: Deal) -> None:
    """Notify about new deal creation."""
    trigger_n8n_webhook("deal.created", {
        "deal_id": deal.id,
        "client_company": deal.client_company,
        "client_email": deal.client_email,
        "client_contact_name": deal.client_contact_name,
        "created_by": deal.created_by.get_full_name() if deal.created_by else "",
    })


def notify_questionnaire_completed(deal: Deal) -> None:
    """Notify when questionnaire is completed for a deal."""
    trigger_n8n_webhook("questionnaire.completed", {
        "deal_id": deal.id,
        "client_company": deal.client_company,
        "phase": deal.phase,
    })


def notify_deal_archived(deal: Deal, reason: str) -> None:
    """Notify when a deal is archived (e.g. max revisions)."""
    trigger_n8n_webhook("deal.archived", {
        "deal_id": deal.id,
        "client_company": deal.client_company,
        "reason": reason,
    })


def notify_proposal_accepted(deal: Deal) -> None:
    """Notify when client accepts a proposal via portal."""
    trigger_n8n_webhook("proposal.accepted", {
        "deal_id": deal.id,
        "client_company": deal.client_company,
        "client_email": deal.client_email,
    })


def notify_proposal_rejected(deal: Deal, feedback: str) -> None:
    """Notify when client rejects a proposal via portal."""
    trigger_n8n_webhook("proposal.rejected", {
        "deal_id": deal.id,
        "client_company": deal.client_company,
        "client_email": deal.client_email,
        "feedback": feedback,
    })


def notify_contract_signed(deal: Deal) -> None:
    """Notify when contract is marked as signed."""
    trigger_n8n_webhook("contract.signed", {
        "deal_id": deal.id,
        "client_company": deal.client_company,
        "client_email": deal.client_email,
    })


def notify_payment_received(payment) -> None:
    """Notify when a payment is marked as paid."""
    trigger_n8n_webhook("payment.received", {
        "deal_id": payment.deal.id,
        "client_company": payment.deal.client_company,
        "amount": str(payment.amount),
        "payment_type": payment.type,
        "invoice_number": payment.invoice_number,
    })


def notify_milestone_approved(milestone) -> None:
    """Notify when client approves a milestone."""
    deal = milestone.project.deal
    trigger_n8n_webhook("milestone.approved", {
        "deal_id": deal.id,
        "milestone_id": milestone.id,
        "milestone_title": milestone.title,
        "client_company": deal.client_company,
    })


def notify_qa_issue_found(milestone, feedback: str) -> None:
    """Notify when QA rejects a milestone."""
    deal = milestone.project.deal
    trigger_n8n_webhook("qa.issue_found", {
        "deal_id": deal.id,
        "milestone_id": milestone.id,
        "milestone_title": milestone.title,
        "client_company": deal.client_company,
        "feedback": feedback,
    })
