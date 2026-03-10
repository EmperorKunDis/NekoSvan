from django.db import models


class Company(models.Model):
    """Firma/klient v CRM"""

    name = models.CharField(max_length=255)
    ico = models.CharField(max_length=20, blank=True)  # IČO
    dic = models.CharField(max_length=20, blank=True)  # DIČ
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default="Česká republika")

    # Kontaktní údaje
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)

    # CRM metadata
    status = models.CharField(
        max_length=20,
        choices=[
            ("lead", "Lead"),
            ("active", "Aktivní"),
            ("inactive", "Neaktivní"),
            ("churned", "Odešel"),
        ],
        default="lead",
    )
    sector = models.CharField(max_length=100, blank=True)  # Odvětví
    tags = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name


class CompanyContact(models.Model):
    """Kontaktní osoba ve firmě"""

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="contacts")
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=100, blank=True)  # Pozice
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    is_primary = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.company.name})"


class Communication(models.Model):
    """Komunikace s firmou"""

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="communications")
    contact = models.ForeignKey(CompanyContact, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(
        max_length=20,
        choices=[
            ("email", "Email"),
            ("phone", "Telefon"),
            ("meeting", "Schůzka"),
            ("note", "Poznámka"),
        ],
    )
    subject = models.CharField(max_length=255)
    content = models.TextField()
    date = models.DateTimeField()
    created_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.type}: {self.subject} ({self.company.name})"


class CompanyDocument(models.Model):
    """Dokument firmy"""

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="documents")
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="company_documents/")
    document_type = models.CharField(max_length=50, blank=True)
    uploaded_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.company.name})"
