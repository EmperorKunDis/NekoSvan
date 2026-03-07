from django.conf import settings
from django.db import models


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        IN_APP = "in_app", "In-app"
        EMAIL = "email", "Email"
        WEBHOOK = "webhook", "Webhook"

    class DeliveryStatus(models.TextChoices):
        PENDING = "pending", "Čeká na odeslání"
        DELIVERED = "delivered", "Doručeno"
        FAILED = "failed", "Selhalo"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    deal = models.ForeignKey(
        "pipeline.Deal",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.URLField(blank=True)
    notification_type = models.CharField(
        max_length=20, choices=NotificationType.choices, default=NotificationType.IN_APP
    )
    delivery_status = models.CharField(
        max_length=20, choices=DeliveryStatus.choices, default=DeliveryStatus.DELIVERED
    )
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "read"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} → {self.user}"
