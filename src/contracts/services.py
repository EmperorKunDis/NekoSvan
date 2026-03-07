import io
import logging
from string import Template

from django.core.files.base import ContentFile

from src.pipeline.models import Deal

from .models import Contract, ContractTemplate

logger = logging.getLogger(__name__)


def generate_contract_pdf(deal: Deal, template: ContractTemplate | None = None) -> Contract:
    """Generate a contract PDF from template and deal data."""
    if template is None:
        template = ContractTemplate.objects.filter(is_active=True).first()
        if template is None:
            raise ValueError("No active contract template found")

    # Get proposal data
    proposal = deal.proposals.filter(status="accepted").first() or deal.proposals.order_by("-version").first()

    # Build template context
    context = {
        "client_name": deal.client_contact_name,
        "client_company": deal.client_company,
        "client_email": deal.client_email,
        "client_phone": deal.client_phone,
        "total_price": str(proposal.total_price) if proposal else "0",
        "deposit_amount": str(proposal.deposit_amount) if proposal else "0",
    }

    # Render template
    body = Template(template.body_template).safe_substitute(context)

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
    except ImportError:
        logger.warning("WeasyPrint not available, generating placeholder PDF")
        pdf_content = body.encode("utf-8")

    filename = f"smlouva_{deal.client_company.lower().replace(' ', '_')}_{deal.id}.pdf"
    contract.generated_pdf.save(filename, ContentFile(pdf_content), save=True)

    return contract
