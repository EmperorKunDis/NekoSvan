"""Service pro zpracování dokumentů a vytvoření leadů pomocí AI."""

import json
import logging
import re
from typing import Any

from django.conf import settings
from django.utils import timezone

from .models import Deal, DealActivity, LeadDocument

logger = logging.getLogger(__name__)


def extract_text_from_file(document: LeadDocument) -> str:
    """Extrahuje text z nahraného souboru."""
    if not document.file:
        return document.raw_text

    file_path = document.file.path
    file_ext = file_path.lower().split(".")[-1]

    try:
        if file_ext == "txt":
            with open(file_path, encoding="utf-8") as f:
                return f.read()
        elif file_ext == "pdf":
            # PyPDF2 nebo pdfplumber
            try:
                import pdfplumber

                with pdfplumber.open(file_path) as pdf:
                    return "\n".join(page.extract_text() or "" for page in pdf.pages)
            except ImportError:
                logger.warning("pdfplumber není nainstalován, PDF nelze zpracovat")
                return ""
        elif file_ext in ("doc", "docx"):
            try:
                import docx

                doc = docx.Document(file_path)
                return "\n".join(p.text for p in doc.paragraphs)
            except ImportError:
                logger.warning("python-docx není nainstalován")
                return ""
        else:
            # Zkusit jako plain text
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                return f.read()
    except Exception as e:
        logger.error(f"Chyba při čtení souboru: {e}")
        return ""


def parse_with_ai(text: str) -> dict[str, Any]:
    """Parsuje text pomocí AI a extrahuje data pro lead."""
    # Fallback na regex parsing pokud AI není dostupné
    return parse_with_regex(text)


def parse_with_regex(text: str) -> dict[str, Any]:
    """Fallback parser pomocí regexů."""
    data: dict[str, Any] = {
        "client_company": "",
        "client_contact_name": "",
        "client_email": "",
        "client_phone": "",
        "description": "",
        "confidence": 0.5,
    }

    # Email
    email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
    if email_match:
        data["client_email"] = email_match.group(0)
        data["confidence"] += 0.1

    # Telefon
    phone_patterns = [
        r"\+420\s*\d{3}\s*\d{3}\s*\d{3}",
        r"\d{3}\s*\d{3}\s*\d{3}",
    ]
    for pattern in phone_patterns:
        phone_match = re.search(pattern, text)
        if phone_match:
            data["client_phone"] = re.sub(r"\s+", "", phone_match.group(0))
            data["confidence"] += 0.1
            break

    # IČO
    ico_match = re.search(r"IČO?:?\s*(\d{8})", text, re.IGNORECASE)
    if ico_match:
        data["client_ico"] = ico_match.group(1)
        data["confidence"] += 0.1

    # Firma - heuristiky
    company_patterns = [
        r"(?:firma|společnost|company)[:\s]+([^\n,]+)",
        r"([A-Z][a-záčďéěíňóřšťúůýž]+(?:\s+[A-Z][a-záčďéěíňóřšťúůýž]+)*)\s+(?:s\.r\.o\.|a\.s\.|k\.s\.|v\.o\.s\.)",
    ]
    for pattern in company_patterns:
        company_match = re.search(pattern, text, re.IGNORECASE)
        if company_match:
            data["client_company"] = company_match.group(1).strip()
            data["confidence"] += 0.15
            break

    # Kontaktní osoba
    name_patterns = [
        r"(?:kontakt|jméno|name)[:\s]+([^\n,]+)",
        r"(?:s pozdravem|regards)[,\s]+([^\n]+)",
    ]
    for pattern in name_patterns:
        name_match = re.search(pattern, text, re.IGNORECASE)
        if name_match:
            data["client_contact_name"] = name_match.group(1).strip()
            data["confidence"] += 0.1
            break

    # Popis - použijeme celý text pokud je krátký, jinak první část
    if len(text) <= 500:
        data["description"] = text.strip()
    else:
        # První odstavec nebo prvních 500 znaků
        first_para = text.split("\n\n")[0]
        data["description"] = first_para[:500].strip()

    return data


def process_document(document: LeadDocument, user=None) -> Deal | None:
    """Zpracuje dokument a vytvoří lead."""
    document.status = LeadDocument.Status.PROCESSING
    document.save(update_fields=["status"])

    try:
        # Extrahovat text
        text = extract_text_from_file(document)
        if not text:
            document.status = LeadDocument.Status.FAILED
            document.error_message = "Nepodařilo se extrahovat text z dokumentu"
            document.save(update_fields=["status", "error_message"])
            return None

        # Parsovat AI/regex
        extracted = parse_with_ai(text)
        document.extracted_data = extracted

        # Validace minimálních dat
        if not extracted.get("client_company") and not extracted.get("client_email"):
            # Pokusit se použít email jako identifikátor
            if extracted.get("client_email"):
                extracted["client_company"] = extracted["client_email"].split("@")[0]
            else:
                document.status = LeadDocument.Status.FAILED
                document.error_message = "Nepodařilo se extrahovat dostatek informací"
                document.save(update_fields=["status", "error_message", "extracted_data"])
                return None

        # Fallbacky
        if not extracted.get("client_company"):
            extracted["client_company"] = "Neznámá firma"
        if not extracted.get("client_contact_name"):
            extracted["client_contact_name"] = "Neznámý kontakt"
        if not extracted.get("client_email"):
            extracted["client_email"] = "neznamy@example.com"

        # Vytvořit deal
        deal = Deal.objects.create(
            client_company=extracted["client_company"],
            client_contact_name=extracted["client_contact_name"],
            client_email=extracted["client_email"],
            client_phone=extracted.get("client_phone", ""),
            client_ico=extracted.get("client_ico", ""),
            description=extracted.get("description", ""),
            phase=Deal.Phase.LEAD,
            created_by=user,
        )

        # Activity log
        DealActivity.objects.create(
            deal=deal,
            user=user,
            action="lead_from_document",
            note=f"Lead vytvořen z dokumentu (confidence: {extracted.get('confidence', 0):.0%})",
        )

        # Update document
        document.deal = deal
        document.status = LeadDocument.Status.PROCESSED
        document.processed_at = timezone.now()
        document.save(update_fields=["deal", "status", "processed_at", "extracted_data"])

        return deal

    except Exception as e:
        logger.exception(f"Chyba při zpracování dokumentu {document.pk}: {e}")
        document.status = LeadDocument.Status.FAILED
        document.error_message = str(e)
        document.save(update_fields=["status", "error_message"])
        return None
