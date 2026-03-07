from django.db import models


class ContractTemplate(models.Model):
    name = models.CharField(max_length=200)
    body_template = models.TextField(
        help_text="Template with placeholders: {{client_name}}, {{total_price}}, {{deposit_amount}}, etc."
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class Contract(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Koncept"
        SENT = "sent", "Odesláno"
        SIGNED = "signed", "Podepsáno"
        CANCELLED = "cancelled", "Zrušeno"

    deal = models.OneToOneField(
        "pipeline.Deal",
        on_delete=models.CASCADE,
        related_name="contract",
    )
    template_used = models.ForeignKey(
        ContractTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    generated_pdf = models.FileField(upload_to="contracts/", blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    signed_by_client = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Smlouva: {self.deal.client_company}"


class Payment(models.Model):
    class PaymentType(models.TextChoices):
        DEPOSIT = "deposit", "Záloha"
        MILESTONE = "milestone", "Milník"
        FINAL = "final", "Doplatek"

    class Status(models.TextChoices):
        PENDING = "pending", "Čeká na platbu"
        PAID = "paid", "Zaplaceno"
        OVERDUE = "overdue", "Po splatnosti"

    deal = models.ForeignKey(
        "pipeline.Deal",
        on_delete=models.CASCADE,
        related_name="payments",
    )
    type = models.CharField(max_length=20, choices=PaymentType.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    paid_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    invoice_number = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_date"]

    def __str__(self) -> str:
        return f"{self.get_type_display()}: {self.amount} Kč — {self.deal.client_company}"
