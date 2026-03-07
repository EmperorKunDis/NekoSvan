import uuid

from django.conf import settings
from django.db import models


class Document(models.Model):
    """Document for ONLYOFFICE editing."""

    class DocumentType(models.TextChoices):
        CONTRACT = "contract", "Smlouva"
        PROPOSAL = "proposal", "Nabídka"
        BRIEF = "brief", "Brief"
        MEETING_NOTES = "meeting_notes", "Poznámky"
        OTHER = "other", "Jiné"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    document_type = models.CharField(
        max_length=20, choices=DocumentType.choices, default=DocumentType.OTHER
    )
    file = models.FileField(upload_to="documents/")
    file_type = models.CharField(max_length=10, default="docx")

    # Relations
    deal = models.ForeignKey(
        "pipeline.Deal",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="documents",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="documents",
    )

    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_documents",
    )
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="modified_documents",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ONLYOFFICE specific
    key = models.CharField(
        max_length=128,
        unique=True,
        help_text="Unique key for ONLYOFFICE document versioning",
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def regenerate_key(self):
        """Generate new key to force ONLYOFFICE to reload document."""
        self.key = str(uuid.uuid4())
        self.save(update_fields=["key"])


class DocumentVersion(models.Model):
    """Version history for documents."""

    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="versions"
    )
    version = models.PositiveIntegerField()
    file = models.FileField(upload_to="documents/versions/")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    changes_description = models.TextField(blank=True)

    class Meta:
        ordering = ["-version"]
        unique_together = ["document", "version"]

    def __str__(self) -> str:
        return f"{self.document.title} v{self.version}"
