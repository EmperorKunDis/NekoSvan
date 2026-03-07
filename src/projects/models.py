from django.conf import settings
from django.db import models


class MilestoneTemplate(models.Model):
    """Reusable milestone templates for different project types."""

    name = models.CharField(max_length=200)
    category = models.CharField(
        max_length=50,
        help_text="Project category key (e.g., custom_dev, website_eshop)",
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Use as default template for this category",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.category})"


class MilestoneTemplateItem(models.Model):
    """Individual milestone items within a template."""

    template = models.ForeignKey(
        MilestoneTemplate,
        on_delete=models.CASCADE,
        related_name="items",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    rich_description = models.TextField(
        blank=True, help_text="HTML/Markdown obsah pro detailní popis"
    )
    deliverables = models.TextField(
        blank=True, help_text="Seznam očekávaných výstupů (jeden na řádek)"
    )
    acceptance_criteria = models.TextField(
        blank=True, help_text="Kritéria pro schválení (jeden na řádek)"
    )
    order = models.PositiveIntegerField(default=0)
    estimated_hours = models.PositiveIntegerField(default=0, blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return f"{self.template.name} — {self.title}"


class TemplateComment(models.Model):
    """Komentáře a připomínky k šablonám."""

    template = models.ForeignKey(
        MilestoneTemplate,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    template_item = models.ForeignKey(
        MilestoneTemplateItem,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="comments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    text = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_template_comments",
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Komentář: {self.template} — {self.user}"


class Project(models.Model):
    class Status(models.TextChoices):
        PLANNING = "planning", "Plánování"
        IN_PROGRESS = "in_progress", "Ve vývoji"
        REVIEW = "review", "Review"
        COMPLETED = "completed", "Dokončeno"
        SUPPORT = "support", "Podpora"

    deal = models.OneToOneField(
        "pipeline.Deal",
        on_delete=models.CASCADE,
        related_name="project",
    )
    implementation_plan = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    estimated_end_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Projekt: {self.deal.client_company}"

    @property
    def progress_percent(self) -> int:
        total = self.milestones.count()
        if total == 0:
            return 0
        approved = self.milestones.filter(status=Milestone.Status.APPROVED).count()
        return int((approved / total) * 100)


class Milestone(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Čeká"
        IN_PROGRESS = "in_progress", "Ve vývoji"
        QA_REVIEW = "qa_review", "QA Review"
        CLIENT_REVIEW = "client_review", "Klient review"
        APPROVED = "approved", "Schváleno"
        REJECTED = "rejected", "Zamítnuto"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="milestones")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    due_date = models.DateField(null=True, blank=True)
    dev_completed_at = models.DateTimeField(null=True, blank=True)
    qa_approved_at = models.DateTimeField(null=True, blank=True)
    client_approved_at = models.DateTimeField(null=True, blank=True)
    client_feedback = models.TextField(blank=True)
    demo_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return f"{self.project.deal.client_company} — {self.title}"


class QAChecklist(models.Model):
    """Final QA checklist for project completion (Fáze 8)."""

    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="qa_checklist")
    checked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="qa_checklists"
    )

    # Checklist items
    performance_ok = models.BooleanField(default=False, verbose_name="Výkon — load time < 3s")
    security_ok = models.BooleanField(default=False, verbose_name="Bezpečnost — OWASP top 10")
    responsive_ok = models.BooleanField(default=False, verbose_name="Responzivita — mobile/tablet/desktop")
    cross_browser_ok = models.BooleanField(default=False, verbose_name="Cross-browser — Chrome/Firefox/Safari")
    seo_ok = models.BooleanField(default=False, verbose_name="SEO — meta tagy, sitemap, robots.txt")
    accessibility_ok = models.BooleanField(default=False, verbose_name="Přístupnost — WCAG 2.1 AA")
    backup_ok = models.BooleanField(default=False, verbose_name="Zálohy — automatické zálohy nastaveny")
    monitoring_ok = models.BooleanField(default=False, verbose_name="Monitoring — uptime + error tracking")
    documentation_ok = models.BooleanField(default=False, verbose_name="Dokumentace — API docs, user guide")
    client_training_ok = models.BooleanField(default=False, verbose_name="Školení klienta — provedeno")

    notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_complete(self) -> bool:
        return all([
            self.performance_ok, self.security_ok, self.responsive_ok,
            self.cross_browser_ok, self.seo_ok, self.accessibility_ok,
            self.backup_ok, self.monitoring_ok, self.documentation_ok,
            self.client_training_ok,
        ])

    @property
    def completion_percent(self) -> int:
        checks = [
            self.performance_ok, self.security_ok, self.responsive_ok,
            self.cross_browser_ok, self.seo_ok, self.accessibility_ok,
            self.backup_ok, self.monitoring_ok, self.documentation_ok,
            self.client_training_ok,
        ]
        return int(sum(checks) / len(checks) * 100)

    def __str__(self) -> str:
        return f"QA Checklist: {self.project.deal.client_company}"


class ProjectComment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="comments")
    milestone = models.ForeignKey(
        Milestone,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="comments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Komentář: {self.project} — {self.user}"
