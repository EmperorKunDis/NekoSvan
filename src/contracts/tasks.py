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
def generate_contract_pdf_task(self, deal_id: int) -> str:
    """Async task to generate contract PDF."""
    from src.pipeline.models import Deal

    from .services import generate_contract_pdf

    logger.info(f"[{self.request.id}] Generating PDF for deal {deal_id}")
    try:
        deal = Deal.objects.get(id=deal_id)
    except Deal.DoesNotExist:
        logger.error(f"[{self.request.id}] Deal {deal_id} not found — permanent failure")
        return ""

    contract = generate_contract_pdf(deal)
    logger.info(f"[{self.request.id}] Contract PDF generated: {contract.generated_pdf.name}")
    return contract.generated_pdf.name


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
def check_overdue_payments(self) -> int:
    """Periodic task: mark overdue payments and send notifications."""
    from django.utils import timezone

    from src.notifications.services import notify_payment_overdue

    from .models import Payment

    logger.info(f"[{self.request.id}] Checking overdue payments")

    today = timezone.now().date()
    overdue_payments = Payment.objects.filter(
        status=Payment.Status.PENDING,
        due_date__lt=today,
    )

    count = 0
    for payment in overdue_payments:
        payment.status = Payment.Status.OVERDUE
        payment.save(update_fields=["status"])
        notify_payment_overdue(payment)
        count += 1

    if count:
        logger.info(f"[{self.request.id}] Marked {count} payments as overdue")
    return count
