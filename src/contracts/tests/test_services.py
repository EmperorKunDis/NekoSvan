import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from src.contracts.models import Contract, ContractTemplate
from src.contracts.services import ContractGenerationError, generate_contract_pdf
from src.pipeline.models import Deal
from src.pricing.models import Proposal


@pytest.fixture
def deal_with_proposal(db):
    """Create a deal with an accepted proposal."""
    deal = Deal.objects.create(
        client_company="Test Company s.r.o.",
        client_contact_name="Jan Novák",
        client_email="jan@test.cz",
        client_phone="+420123456789",
        phase=Deal.Phase.CONTRACT,
    )
    Proposal.objects.create(
        deal=deal,
        version=1,
        status="accepted",
        total_price=100000,
        deposit_amount=30000,
    )
    return deal


@pytest.fixture
def template_dollar_syntax(db):
    """Template using $variable syntax."""
    return ContractTemplate.objects.create(
        name="Test Template (Dollar)",
        body_template="<h1>Smlouva</h1><p>Klient: $client_name ($client_company)</p><p>Cena: $total_price Kč</p>",
        is_active=True,
    )


@pytest.fixture
def template_braces_syntax(db):
    """Template using {{variable}} syntax."""
    return ContractTemplate.objects.create(
        name="Test Template (Braces)",
        body_template="<h1>Smlouva</h1><p>Klient: {{client_name}} ({{client_company}})</p><p>Cena: {{total_price}} Kč</p>",
        is_active=False,  # Not active by default
    )


@pytest.mark.django_db
class TestContractGeneration:
    def test_generate_with_dollar_syntax(self, deal_with_proposal, template_dollar_syntax):
        """Test PDF generation with $variable template syntax."""
        contract = generate_contract_pdf(deal_with_proposal, template_dollar_syntax)
        
        assert contract.deal == deal_with_proposal
        assert contract.template_used == template_dollar_syntax
        assert contract.generated_pdf.name
        assert "smlouva_test_company_s.r.o." in contract.generated_pdf.name

    def test_generate_with_braces_syntax(self, deal_with_proposal, template_braces_syntax):
        """Test PDF generation with {{variable}} template syntax."""
        contract = generate_contract_pdf(deal_with_proposal, template_braces_syntax)
        
        assert contract.deal == deal_with_proposal
        assert contract.template_used == template_braces_syntax
        assert contract.generated_pdf.name

    def test_no_active_template_raises_error(self, deal_with_proposal, template_braces_syntax):
        """Test that missing active template raises ValueError."""
        # template_braces_syntax is not active
        with pytest.raises(ValueError, match="No active contract template found"):
            generate_contract_pdf(deal_with_proposal)

    def test_missing_proposal_uses_zero_values(self, db, template_dollar_syntax):
        """Test that missing proposal doesn't crash, uses zero values."""
        deal = Deal.objects.create(
            client_company="No Proposal Company",
            phase=Deal.Phase.CONTRACT,
        )
        
        contract = generate_contract_pdf(deal, template_dollar_syntax)
        assert contract.deal == deal
        # Should not raise error, just log warning

    def test_contract_reuses_existing(self, deal_with_proposal, template_dollar_syntax):
        """Test that regenerating contract reuses existing Contract object."""
        contract1 = generate_contract_pdf(deal_with_proposal, template_dollar_syntax)
        contract2 = generate_contract_pdf(deal_with_proposal, template_dollar_syntax)
        
        assert contract1.id == contract2.id
        assert Contract.objects.filter(deal=deal_with_proposal).count() == 1
