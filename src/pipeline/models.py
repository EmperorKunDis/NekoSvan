import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

# Default expiration periods for portal tokens
PORTAL_TOKEN_DEFAULT_DAYS = 90
PORTAL_TOKEN_ARCHIVED_DAYS = 30


class ClientCompany(models.Model):
    """Structured client company data (replaces flat fields on Deal)."""

    name = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    ico = models.CharField("IČO", max_length=20, blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "client companies"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Deal(models.Model):
    class Phase(models.TextChoices):
        LEAD = "lead", "Lead"
        QUALIFICATION = "qualification", "Kvalifikace"
        PRICING = "pricing", "Cenotvorba"
        PRESENTATION = "presentation", "Prezentace"
        CONTRACT = "contract", "Smlouva"
        PLANNING = "planning", "Plánování"
        DEVELOPMENT = "development", "Vývoj"
        COMPLETED = "completed", "Dokončeno"

    class Status(models.TextChoices):
        ACTIVE = "active", "Aktivní"
        ARCHIVED = "archived", "Archivováno"
        ON_HOLD = "on_hold", "Pozastaveno"

    # Client info (structured — preferred)
    client = models.ForeignKey(
        ClientCompany,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deals",
    )

    # Client info (flat — deprecated, kept for backward compat)
    client_company = models.CharField(max_length=200)
    client_contact_name = models.CharField(max_length=200)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=20, blank=True)
    client_ico = models.CharField("IČO", max_length=20, blank=True)
    description = models.TextField(blank=True)

    # Pipeline state
    phase = models.CharField(max_length=20, choices=Phase.choices, default=Phase.LEAD)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_deals",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_deals",
    )

    # Pricing revisions
    revision_count = models.PositiveIntegerField(default=0)

    # Client portal token
    portal_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    portal_token_expires_at = models.DateTimeField(null=True, blank=True)
    portal_token_last_accessed_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    phase_changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["phase", "status"]),
            models.Index(fields=["assigned_to", "status"]),
            models.Index(fields=["portal_token"]),
        ]

    def __str__(self) -> str:
        return f"{self.client_company} — {self.get_phase_display()}"

    def get_client_data(self) -> dict:
        """Return client data from FK if available, otherwise from flat fields."""
        if self.client:
            return {
                "company": self.client.name,
                "contact_name": self.client.contact_name,
                "email": self.client.email,
                "phone": self.client.phone,
                "ico": self.client.ico,
            }
        return {
            "company": self.client_company,
            "contact_name": self.client_contact_name,
            "email": self.client_email,
            "phone": self.client_phone,
            "ico": self.client_ico,
        }

    def is_portal_token_valid(self) -> bool:
        """Check if portal token is still valid. None expires_at = always valid (backward compat)."""
        if self.portal_token_expires_at is None:
            return True
        return timezone.now() < self.portal_token_expires_at

    def refresh_portal_token(self, days: int = PORTAL_TOKEN_DEFAULT_DAYS) -> None:
        """Generate a new portal token with fresh expiration."""
        self.portal_token = uuid.uuid4()
        self.portal_token_expires_at = timezone.now() + timedelta(days=days)
        self.save(update_fields=["portal_token", "portal_token_expires_at", "updated_at"])

    def save(self, *args, **kwargs):
        # Set default expiration for new deals
        if not self.pk and self.portal_token_expires_at is None:
            self.portal_token_expires_at = timezone.now() + timedelta(days=PORTAL_TOKEN_DEFAULT_DAYS)
        super().save(*args, **kwargs)


class DealActivity(models.Model):
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name="activities")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    action = models.CharField(max_length=100)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "deal activities"

    def __str__(self) -> str:
        return f"{self.deal} — {self.action}"


class LeadDocument(models.Model):
    """Dokument pro automatické vytvoření leadu."""

    class DocumentType(models.TextChoices):
        EMAIL = "email", "Email"
        BRIEF = "brief", "Brief"
        RFP = "rfp", "RFP"
        MEETING_NOTES = "meeting_notes", "Poznámky ze schůzky"
        OTHER = "other", "Jiné"

    class Status(models.TextChoices):
        PENDING = "pending", "Čeká na zpracování"
        PROCESSING = "processing", "Zpracovává se"
        PROCESSED = "processed", "Zpracováno"
        FAILED = "failed", "Chyba"

    file = models.FileField(upload_to="lead_documents/", blank=True, null=True)
    raw_text = models.TextField(
        blank=True, help_text="Vložený text (pokud není soubor)"
    )
    document_type = models.CharField(
        max_length=20, choices=DocumentType.choices, default=DocumentType.OTHER
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )

    # AI extracted data
    extracted_data = models.JSONField(
        default=dict, blank=True, help_text="Data extrahovaná AI"
    )

    # Resulting deal
    deal = models.ForeignKey(
        Deal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_documents",
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    def __str__(self) -> str:
        if self.file:
            return f"Dokument: {self.file.name}"
        return f"Text: {self.raw_text[:50]}..."
