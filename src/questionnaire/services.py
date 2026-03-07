import io
import json
import logging

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)

OLLAMA_TIMEOUT = 60

SYSTEM_PROMPT = """\
You are a structured data extraction assistant. Given a text about a client or project,
extract as many relevant fields as possible into a JSON object.

The fields correspond to a questionnaire with these sections:

Section A - Client & context:
- a_company_name (string)
- a_ico (string, Czech IČO)
- a_contact_person (string)
- a_email (string)
- a_phone (string)
- a_industry (one of: it, eshop, manufacturing, finance, healthcare, education, realestate, logistics, gastro, services, nonprofit, government, other)
- a_employee_count (one of: solo, micro, small, medium, large)
- a_annual_revenue (one of: under_1m, 1_10m, 10_50m, 50_200m, over_200m)
- a_current_it (list of: website, eshop, crm, erp, accounting, project_mgmt, custom_app, ai_tools, none)

Section B - Project type:
- b_main_categories (list of: custom_dev, website_eshop, ai_automation, enterprise_system, integration, security, data_analytics, support, training, mobile_app, cloud_migration, iot, blockchain, other)
- b_primary_goal (one of: new_product, digitize, replace, optimize, automate, data, security, other)
- b_target_users (list of: employees, management, clients, partners, public)
- b_estimated_users (one of: 1_5, 6_20, 21_50, 51_200, 201_1000, 1001_plus, public)

Section K - Budget & timeline:
- k_budget_range (one of: under_50k, 50_100k, 100_250k, 250_500k, 500k_1m, 1m_3m, over_3m, unknown)
- k_launch_deadline (one of: asap, 1month, 3months, 6months, year, flexible)

Section M - Conclusion:
- m_lead_source (one of: referral, google, social, event, cold, returning, other)
- m_lead_rating (one of: hot, warm, cool, cold)
- m_sales_notes (string, any extra notes)

For other sections (C-J, L), extract relevant fields if information is available.

Rules:
- Only include fields where you have reasonable confidence.
- Use EXACTLY the values listed in parentheses for choice fields.
- For list fields, return a JSON array of strings.
- Return ONLY a valid JSON object, no markdown, no explanation.
- If you cannot extract any fields, return {}.
"""


def extract_text_from_file(uploaded_file) -> str:
    """Extract text content from uploaded file (PDF, DOCX, TXT)."""
    name = uploaded_file.name.lower()
    content = uploaded_file.read()

    if name.endswith(".txt"):
        return content.decode("utf-8", errors="replace")

    if name.endswith(".pdf"):
        try:
            from PyPDF2 import PdfReader

            reader = PdfReader(io.BytesIO(content))
            return "\n".join(
                page.extract_text() or "" for page in reader.pages
            )
        except ImportError:
            logger.warning("PyPDF2 not installed, cannot extract PDF text")
            return ""

    if name.endswith((".docx", ".doc")):
        try:
            from docx import Document

            doc = Document(io.BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs)
        except ImportError:
            logger.warning("python-docx not installed, cannot extract DOCX text")
            return ""

    return content.decode("utf-8", errors="replace")


def extract_from_text(text: str) -> dict:
    """Send text to local Ollama and return structured questionnaire data."""
    base_url = getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434")
    model = getattr(settings, "OLLAMA_MODEL", "llama3.1")

    try:
        response = httpx.post(
            f"{base_url}/api/generate",
            json={
                "model": model,
                "system": SYSTEM_PROMPT,
                "prompt": f"Extract questionnaire data from this text:\n\n{text}",
                "stream": False,
                "format": "json",
            },
            timeout=OLLAMA_TIMEOUT,
        )
        response.raise_for_status()
    except httpx.ConnectError:
        logger.error("Cannot connect to Ollama at %s", base_url)
        raise OllamaUnavailableError(
            f"Cannot connect to Ollama at {base_url}. Is it running?"
        )
    except httpx.TimeoutException:
        logger.error("Ollama request timed out after %ds", OLLAMA_TIMEOUT)
        raise OllamaUnavailableError("Ollama request timed out.")
    except httpx.HTTPStatusError as e:
        logger.error("Ollama returned HTTP %d", e.response.status_code)
        raise OllamaUnavailableError(f"Ollama error: HTTP {e.response.status_code}")

    raw_response = response.json().get("response", "{}")

    try:
        extracted = json.loads(raw_response)
    except json.JSONDecodeError:
        logger.warning("Ollama returned invalid JSON: %s", raw_response[:200])
        return {}

    return _sanitize_extracted(extracted)


def _sanitize_extracted(data: dict) -> dict:
    """Remove unknown keys and validate choice values."""
    from .models import QuestionnaireResponse
    from .serializers import ARRAY_FIELD_VALIDATORS

    valid_fields = {f.name for f in QuestionnaireResponse._meta.get_fields()}
    # Remove meta/relation fields
    valid_fields -= {"deal", "filled_by", "filled_at", "id"}

    sanitized = {}
    for key, value in data.items():
        if key not in valid_fields:
            continue

        # Validate array field values
        if key in ARRAY_FIELD_VALIDATORS:
            if isinstance(value, list):
                valid_values = ARRAY_FIELD_VALIDATORS[key]
                sanitized[key] = [v for v in value if v in valid_values]
            continue

        sanitized[key] = value

    return sanitized


class OllamaUnavailableError(Exception):
    pass
