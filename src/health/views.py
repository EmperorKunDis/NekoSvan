import logging

import requests
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """Health check endpoint for monitoring and Docker healthchecks."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        checks = {}
        is_healthy = True

        # Database (critical)
        try:
            connection.ensure_connection()
            checks["database"] = "ok"
        except Exception as e:
            checks["database"] = f"error: {e}"
            is_healthy = False

        # Redis / Cache (critical)
        try:
            cache.set("health_check", "ok", timeout=10)
            val = cache.get("health_check")
            checks["redis"] = "ok" if val == "ok" else "error: unexpected value"
            if val != "ok":
                is_healthy = False
        except Exception as e:
            checks["redis"] = f"error: {e}"
            is_healthy = False

        # Celery (critical) — ping via Redis
        try:
            from config.celery import app as celery_app

            result = celery_app.control.ping(timeout=2)
            checks["celery"] = "ok" if result else "no workers"
            if not result:
                is_healthy = False
        except Exception as e:
            checks["celery"] = f"error: {e}"
            is_healthy = False

        # ONLYOFFICE (optional)
        onlyoffice_url = getattr(settings, "ONLYOFFICE_URL", "")
        if onlyoffice_url:
            try:
                resp = requests.get(f"{onlyoffice_url}/healthcheck", timeout=5)
                checks["onlyoffice"] = "ok" if resp.status_code == 200 else f"status {resp.status_code}"
            except Exception:
                checks["onlyoffice"] = "unavailable"

        # Ollama (optional)
        ollama_url = getattr(settings, "OLLAMA_BASE_URL", "")
        if ollama_url:
            try:
                resp = requests.get(ollama_url, timeout=5)
                checks["ollama"] = "ok" if resp.status_code == 200 else f"status {resp.status_code}"
            except Exception:
                checks["ollama"] = "unavailable"

        status_code = 200 if is_healthy else 503
        return JsonResponse({"status": "healthy" if is_healthy else "degraded", "checks": checks}, status=status_code)
