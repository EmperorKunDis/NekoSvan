import io
import logging
from string import Template

from django.core.files.base import ContentFile

from src.pipeline.models import Deal

from .models import Contract, ContractTemplate

logger = logging.getLogger(__name__)


class ContractGenerationError(Exception):
    """Exception raised when contract PDF generation fails."""

    pass


def generate_contract_pdf(deal: Deal, template: ContractTemplate | None = None) -> Contract:
    """Generate a contract PDF from template and deal data."""
    if template is None:
        template = ContractTemplate.objects.filter(is_active=True).first()
        if template is None:
            logger.error("No active contract template found in database")
            raise ValueError("Nebyla nalezena žádná aktivní šablona smlouvy")

    # Get proposal data
    proposal = deal.proposals.filter(status="accepted").first() or deal.proposals.order_by("-version").first()
    if not proposal:
        logger.warning(f"No proposal found for deal {deal.id}, using zero values")

    # Build template context
    context = {
        "client_name": deal.client_contact_name or "N/A",
        "client_company": deal.client_company or "N/A",
        "client_email": deal.client_email or "N/A",
        "client_phone": deal.client_phone or "N/A",
        "total_price": str(proposal.total_price) if proposal else "0",
        "deposit_amount": str(proposal.deposit_amount) if proposal else "0",
    }

    # Render template - support both $variable and {{variable}} syntax
    try:
        body = Template(template.body_template).safe_substitute(context)
        # Also handle Django/Jinja2-style {{variable}} placeholders
        for key, value in context.items():
            body = body.replace(f"{{{{{key}}}}}", str(value))
    except Exception as e:
        logger.error(f"Template rendering failed for deal {deal.id}: {e}")
        raise ContractGenerationError(f"Vykreslení šablony selhalo: {e}")

    # Generate PDF using WeasyPrint
    contract, _created = Contract.objects.get_or_create(
        deal=deal,
        defaults={"template_used": template},
    )

    try:
        from weasyprint import HTML

        html_content = f"""
        <html>
        <head><meta charset="utf-8"><style>
            body {{ font-family: sans-serif; margin: 40px; line-height: 1.6; }}
            h1 {{ color: #333; }}
        </style></head>
        <body>{body}</body>
        </html>
        """
        pdf_buffer = io.BytesIO()
        HTML(string=html_content).write_pdf(pdf_buffer)
        pdf_content = pdf_buffer.getvalue()
        logger.info(f"PDF successfully generated for deal {deal.id}")
    except ImportError:
        logger.warning("WeasyPrint not available, generating placeholder PDF")
        pdf_content = body.encode("utf-8")
    except Exception as e:
        logger.error(f"WeasyPrint PDF generation failed for deal {deal.id}: {e}", exc_info=True)
        raise ContractGenerationError(f"Generování PDF selhalo: {e}")

    filename = f"smlouva_{deal.client_company.lower().replace(' ', '_')}_{deal.id}.pdf"
    contract.generated_pdf.save(filename, ContentFile(pdf_content), save=True)
    contract.template_used = template
    contract.save(update_fields=["template_used", "updated_at"])

    return contract
