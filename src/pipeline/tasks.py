import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=60,
    retry_backoff_max=600,
    max_retries=3,
    soft_time_limit=120,
    time_limit=180,
    acks_late=True,
)
def check_inactive_deals(self) -> int:
    """Periodic task: remind assignees about deals inactive for 48+ hours."""
    from datetime import timedelta

    from django.utils import timezone

    from src.notifications.services import create_notification, trigger_n8n_webhook

    from .models import Deal

    logger.info(f"[{self.request.id}] Checking inactive deals")

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
        logger.info(f"[{self.request.id}] Sent {count} inactivity reminders")
    return count
