from decimal import Decimal

from django.conf import settings
from django.db import models


class PricingMatrix(models.Model):
    """Configurable pricing matrix for auto-calculation."""

    category = models.CharField(max_length=50, unique=True, help_text="Category key (e.g., custom_dev)")
    category_label = models.CharField(max_length=100, help_text="Display label")
    base_hours = models.PositiveIntegerField(default=80)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("1500"))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category"]
        verbose_name_plural = "Pricing matrices"

    def __str__(self) -> str:
        return f"{self.category_label} ({self.base_hours}h @ {self.hourly_rate} CZK)"


class PricingModifier(models.Model):
    """Modifiers that affect final pricing (user count, complexity, etc.)."""

    class ModifierType(models.TextChoices):
        USER_COUNT = "user_count", "User Count"
        COMPLEXITY = "complexity", "Complexity"
        DESIGN = "design", "Design Requirements"
        PLATFORM = "platform", "Platform"

    modifier_type = models.CharField(max_length=20, choices=ModifierType.choices)
    key = models.CharField(max_length=50, help_text="Value key (e.g., 1_5, 6_20)")
    label = models.CharField(max_length=100)
    multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("1.0"))
    extra_hours = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["modifier_type", "key"]
        unique_together = [("modifier_type", "key")]

    def __str__(self) -> str:
        return f"{self.get_modifier_type_display()}: {self.label} (×{self.multiplier})"


class Proposal(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Koncept"
        SENT = "sent", "Odesláno"
        ACCEPTED = "accepted", "Přijato"
        REJECTED = "rejected", "Zamítnuto"
        EXPIRED = "expired", "Expirováno"

    deal = models.ForeignKey(
        "pipeline.Deal",
        on_delete=models.CASCADE,
        related_name="proposals",
    )
    version = models.PositiveIntegerField(default=1)
    base_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    items = models.JSONField(
        default=list,
        blank=True,
        help_text='[{"name": "...", "hours": 10, "rate": 1500, "total": 15000}]',
    )
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deposit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    demo_url = models.URLField(blank=True)
    demo_description = models.TextField(blank=True)
    valid_until = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    client_feedback = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_proposals",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-version"]
        unique_together = [("deal", "version")]

    def __str__(self) -> str:
        return f"Nabídka {self.deal.client_company} v{self.version}"
