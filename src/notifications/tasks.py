import logging

import requests
from celery import shared_task
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

CIRCUIT_BREAKER_KEY = "n8n_circuit_breaker"
CIRCUIT_BREAKER_FAILURES_KEY = "n8n_circuit_failures"
CIRCUIT_BREAKER_THRESHOLD = 5
CIRCUIT_BREAKER_TIMEOUT = 300  # 5 minutes


def _is_circuit_open() -> bool:
    return cache.get(CIRCUIT_BREAKER_KEY, False)


def _record_failure():
    failures = cache.get(CIRCUIT_BREAKER_FAILURES_KEY, 0) + 1
    cache.set(CIRCUIT_BREAKER_FAILURES_KEY, failures, timeout=CIRCUIT_BREAKER_TIMEOUT)
    if failures >= CIRCUIT_BREAKER_THRESHOLD:
        cache.set(CIRCUIT_BREAKER_KEY, True, timeout=CIRCUIT_BREAKER_TIMEOUT)
        logger.warning(f"N8N circuit breaker OPEN after {failures} failures")


def _record_success():
    cache.delete(CIRCUIT_BREAKER_KEY)
    cache.delete(CIRCUIT_BREAKER_FAILURES_KEY)


@shared_task(
    bind=True,
    autoretry_for=(requests.RequestException,),
    retry_backoff=30,
    retry_backoff_max=300,
    max_retries=5,
    soft_time_limit=30,
    time_limit=60,
    acks_late=True,
)
def send_n8n_webhook(self, event: str, payload: dict) -> bool:
    """Send event to N8N webhook with circuit breaker protection."""
    if _is_circuit_open():
        logger.warning(f"[{self.request.id}] N8N circuit breaker open, skipping: {event}")
        return False

    base_url = getattr(settings, "N8N_WEBHOOK_BASE_URL", "")
    if not base_url:
        logger.warning(f"[{self.request.id}] N8N_WEBHOOK_BASE_URL not configured, skipping: {event}")
        return False

    url = f"{base_url}/{event}"
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        _record_success()
        return True
    except requests.RequestException:
        _record_failure()
        raise
