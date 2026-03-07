import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def generate_contract_pdf_task(deal_id: int) -> str:
    """Async task to generate contract PDF."""
    from src.pipeline.models import Deal

    from .services import generate_contract_pdf

    deal = Deal.objects.get(id=deal_id)
    contract = generate_contract_pdf(deal)
    logger.info(f"Contract PDF generated for deal {deal_id}: {contract.generated_pdf.name}")
    return contract.generated_pdf.name


@shared_task
def check_overdue_payments() -> int:
    """Periodic task: mark overdue payments and send notifications."""
    from django.utils import timezone

    from src.notifications.services import notify_payment_overdue

    from .models import Payment

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
        logger.info(f"Marked {count} payments as overdue")
    return count
