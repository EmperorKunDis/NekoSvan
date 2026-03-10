"""Business logic for companies app."""

from typing import Optional

from django.db.models import Count, Q, QuerySet

from .models import Communication, Company, CompanyContact, CompanyDocument


def get_company_queryset(
    status: Optional[str] = None,
    sector: Optional[str] = None,
    search: Optional[str] = None,
) -> QuerySet[Company]:
    """Get filtered company queryset with counts."""
    queryset = Company.objects.annotate(
        contacts_count=Count("contacts", distinct=True),
        deals_count=Count("deals", distinct=True),
    )

    if status:
        queryset = queryset.filter(status=status)

    if sector:
        queryset = queryset.filter(sector__icontains=sector)

    if search:
        queryset = queryset.filter(
            Q(name__icontains=search)
            | Q(ico__icontains=search)
            | Q(dic__icontains=search)
            | Q(email__icontains=search)
            | Q(city__icontains=search)
        )

    return queryset


def create_company(data: dict, created_by=None) -> Company:
    """Create a new company."""
    company = Company.objects.create(**data)
    return company


def update_company(company: Company, data: dict) -> Company:
    """Update company fields."""
    for field, value in data.items():
        setattr(company, field, value)
    company.save()
    return company


def create_communication(
    company: Company,
    type: str,
    subject: str,
    content: str,
    date,
    created_by=None,
    contact: Optional[CompanyContact] = None,
) -> Communication:
    """Create a communication record."""
    return Communication.objects.create(
        company=company,
        contact=contact,
        type=type,
        subject=subject,
        content=content,
        date=date,
        created_by=created_by,
    )


def create_contact(company: Company, data: dict) -> CompanyContact:
    """Create a contact for a company."""
    contact = CompanyContact.objects.create(company=company, **data)

    # If this is marked as primary, unset other primary contacts
    if contact.is_primary:
        CompanyContact.objects.filter(company=company).exclude(pk=contact.pk).update(is_primary=False)

    return contact


def update_contact(contact: CompanyContact, data: dict) -> CompanyContact:
    """Update contact fields."""
    for field, value in data.items():
        setattr(contact, field, value)

    # If this is marked as primary, unset other primary contacts
    if contact.is_primary:
        CompanyContact.objects.filter(company=contact.company).exclude(pk=contact.pk).update(is_primary=False)

    contact.save()
    return contact


def get_primary_contact(company: Company) -> Optional[CompanyContact]:
    """Get the primary contact for a company."""
    return company.contacts.filter(is_primary=True).first()


def upload_document(company: Company, file, name: str, document_type: str = "", uploaded_by=None) -> CompanyDocument:
    """Upload a document for a company."""
    return CompanyDocument.objects.create(
        company=company,
        file=file,
        name=name,
        document_type=document_type,
        uploaded_by=uploaded_by,
    )
