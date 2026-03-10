from django.utils import timezone

from src.pipeline.models import Deal, DealActivity


def log_portal_access(deal: Deal, request, action: str) -> None:
    """Log portal access as a DealActivity and update last_accessed_at."""
    ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
    if not ip:
        ip = request.META.get("REMOTE_ADDR", "unknown")
    user_agent = request.META.get("HTTP_USER_AGENT", "")[:200]

    DealActivity.objects.create(
        deal=deal,
        user=None,
        action=f"portal:{action}",
        note=f"IP: {ip} | UA: {user_agent}",
    )

    deal.portal_token_last_accessed_at = timezone.now()
    deal.save(update_fields=["portal_token_last_accessed_at"])
