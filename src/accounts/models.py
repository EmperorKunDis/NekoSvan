from django.contrib.auth.models import AbstractUser
from django.db import models


class Company(models.Model):
    class CompanyName(models.TextChoices):
        ADNP = "adnp", "ADNP"
        NEKOSVAN = "nekosvan", "NekoSvan"
        PRAUT = "praut", "Praut"

    name = models.CharField(max_length=20, choices=CompanyName.choices, unique=True)
    legal_name = models.CharField(max_length=200)
    ico = models.CharField("IČO", max_length=20, blank=True)
    dic = models.CharField("DIČ", max_length=20, blank=True)
    address = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "companies"

    def __str__(self) -> str:
        return self.get_name_display()


class User(AbstractUser):
    class Role(models.TextChoices):
        ADAM = "adam", "Adam (ADNP)"
        VADIM = "vadim", "Vadim"
        MARTIN = "martin", "Martin (Praut)"
        NEKOSVAN = "nekosvan", "NekoSvan"
        CLIENT = "client", "Klient"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT)
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
    )
    phone = models.CharField(max_length=20, blank=True)
    is_master = models.BooleanField(
        default=False,
        help_text="Master může vytvářet členy týmu se stejnou rolí",
    )
    created_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_users",
    )
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.get_full_name()} ({self.get_role_display()})"

    def can_create_team_member(self) -> bool:
        """Master může vytvářet členy týmu."""
        return self.is_master

    def get_team_members(self):
        """Vrátí všechny členy se stejnou rolí."""
        if not self.is_master:
            return User.objects.none()
        return User.objects.filter(role=self.role).exclude(pk=self.pk)
