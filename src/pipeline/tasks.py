import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def check_inactive_deals() -> int:
    """Periodic task: remind assignees about deals inactive for 48+ hours."""
    from datetime import timedelta

    from django.utils import timezone

    from src.notifications.services import create_notification, trigger_n8n_webhook

    from .models import Deal

    cutoff = timezone.now() - timedelta(hours=48)
    inactive_deals = Deal.objects.filter(
        status=Deal.Status.ACTIVE,
        updated_at__lt=cutoff,
    ).exclude(
        phase=Deal.Phase.COMPLETED,
    ).select_related("assigned_to")

    count = 0
    for deal in inactive_deals:
        if not deal.assigned_to:
            continue

        create_notification(
            user=deal.assigned_to,
            title=f"Reminder: {deal.client_company}",
            message=f"Deal {deal.client_company} čeká na akci ve fázi {deal.get_phase_display()} už 48+ hodin.",
            deal=deal,
        )

        trigger_n8n_webhook("deal.inactive_48h", {
            "deal_id": deal.id,
            "client_company": deal.client_company,
            "phase": deal.phase,
            "assigned_to_email": deal.assigned_to.email,
            "assigned_to_name": deal.assigned_to.get_full_name(),
            "hours_inactive": int((timezone.now() - deal.updated_at).total_seconds() / 3600),
        })

        count += 1

    if count:
        logger.info(f"Sent {count} inactivity reminders")
    return count
