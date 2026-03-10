import logging

import jwt
from django.conf import settings

logger = logging.getLogger(__name__)


def _get_secret() -> str:
    return getattr(settings, "ONLYOFFICE_JWT_SECRET", "")


def generate_onlyoffice_token(payload: dict) -> str:
    """Generate a JWT token for ONLYOFFICE. Returns empty string if secret not configured."""
    secret = _get_secret()
    if not secret:
        return ""
    return jwt.encode(payload, secret, algorithm="HS256")


def verify_onlyoffice_token(token: str) -> dict | None:
    """Verify a JWT token from ONLYOFFICE. Returns None if invalid, {} if secret not configured."""
    secret = _get_secret()
    if not secret:
        return {}
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        logger.warning("Invalid ONLYOFFICE JWT token")
        return None
