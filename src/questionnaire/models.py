from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models


class QuestionnaireResponse(models.Model):
    """Comprehensive questionnaire with sections A–M (~84 fields).

    Conditional visibility is handled on frontend.
    Backend stores all submitted fields; conditional section fields are blank=True.
    """

    # ── Section A: Client & context ──────────────────────────────────

    class Industry(models.TextChoices):
        IT = "it", "IT / Software"
        ESHOP = "eshop", "E-commerce / E-shop"
        MANUFACTURING = "manufacturing", "Výroba / Průmysl"
        FINANCE = "finance", "Finance / Pojišťovnictví"
        HEALTHCARE = "healthcare", "Zdravotnictví"
        EDUCATION = "education", "Vzdělávání"
        REALESTATE = "realestate", "Reality / Stavebnictví"
        LOGISTICS = "logistics", "Logistika / Doprava"
        GASTRO = "gastro", "Gastronomie / HoReCa"
        SERVICES = "services", "Služby / Poradenství"
        NONPROFIT = "nonprofit", "Neziskový sektor"
        GOVERNMENT = "government", "Státní správa"
        OTHER = "other", "Jiné"

    class EmployeeCount(models.TextChoices):
        SOLO = "solo", "Jednotlivec / freelancer"
        MICRO = "micro", "2–10"
        SMALL = "small", "11–50"
        MEDIUM = "medium", "51–250"
        LARGE = "large", "250+"

    class AnnualRevenue(models.TextChoices):
        UNDER_1M = "under_1m", "Pod 1 mil. Kč"
        R1_10M = "1_10m", "1–10 mil. Kč"
        R10_50M = "10_50m", "10–50 mil. Kč"
        R50_200M = "50_200m", "50–200 mil. Kč"
        OVER_200M = "over_200m", "Nad 200 mil. Kč"

    class ITSatisfaction(models.TextChoices):
        SATISFIED = "satisfied", "Spokojeni"
        PARTIAL = "partial", "Částečně spokojeni"
        DISSATISFIED = "dissatisfied", "Nespokojeni"
        NO_IT = "no_it", "Nemáme IT řešení"

    a_company_name = models.CharField("Company name", max_length=200, blank=True)
    a_ico = models.CharField("IČO", max_length=20, blank=True)
    a_contact_person = models.CharField("Contact person", max_length=200, blank=True)
    a_email = models.EmailField("Email", blank=True)
    a_phone = models.CharField("Phone", max_length=20, blank=True)
    a_industry = models.CharField(
        max_length=20, choices=Industry.choices, blank=True
    )
    a_industry_other = models.CharField(max_length=200, blank=True)
    a_employee_count = models.CharField(
        max_length=20, choices=EmployeeCount.choices, blank=True
    )
    a_annual_revenue = models.CharField(
        max_length=20, choices=AnnualRevenue.choices, blank=True
    )
    a_current_it = ArrayField(
        models.CharField(max_length=40),
        default=list,
        blank=True,
        help_text="Multi-select: website, eshop, crm, erp, accounting, "
        "project_mgmt, custom_app, ai_tools, none",
    )
    a_it_satisfaction = models.CharField(
        max_length=20, choices=ITSatisfaction.choices, blank=True
    )

    # ── Section B: Project type ──────────────────────────────────────

    class PrimaryGoal(models.TextChoices):
        NEW_PRODUCT = "new_product", "Nový produkt / služba"
        DIGITIZE = "digitize", "Digitalizace procesů"
        REPLACE = "replace", "Náhrada stávajícího systému"
        OPTIMIZE = "optimize", "Optimalizace / zrychlení"
        AUTOMATE = "automate", "Automatizace"
        DATA = "data", "Lepší práce s daty"
        SECURITY = "security", "Zvýšení bezpečnosti"
        OTHER = "other", "Jiné"

    class EstimatedUsers(models.TextChoices):
        U1_5 = "1_5", "1–5"
        U6_20 = "6_20", "6–20"
        U21_50 = "21_50", "21–50"
        U51_200 = "51_200", "51–200"
        U201_1000 = "201_1000", "201–1 000"
        U1001_PLUS = "1001_plus", "1 000+"
        PUBLIC = "public", "Veřejnost (neomezeno)"

    b_main_categories = ArrayField(
        models.CharField(max_length=40),
        default=list,
        blank=True,
        help_text="Multi-select: custom_dev, website_eshop, ai_automation, "
        "enterprise_system, integration, security, data_analytics, "
        "support, training, mobile_app, cloud_migration, iot, "
        "blockchain, other",
    )
    b_primary_goal = models.CharField(
        max_length=20, choices=PrimaryGoal.choices, blank=True
    )
    b_target_users = ArrayField(
        models.CharField(max_length=30),
        default=list,
        blank=True,
        help_text="Multi-select: employees, management, clients, partners, public",
    )
    b_estimated_users = models.CharField(
        max_length=20, choices=EstimatedUsers.choices, blank=True
    )

    # ── Section C: Custom development (conditional: custom_dev in B1) ─

    class OfflineMode(models.TextChoices):
        YES = "yes", "Ano"
        NO = "no", "Ne"
        PARTIAL = "partial", "Částečně"

    class YesNo(models.TextChoices):
        YES = "yes", "Ano"
        NO = "no", "Ne"

    class YesNoPartial(models.TextChoices):
        YES = "yes", "Ano"
        NO = "no", "Ne"
        PARTIAL = "partial", "Částečně"

    class HasDesign(models.TextChoices):
        YES_FIGMA = "yes_figma", "Ano, v Figmě"
        YES_OTHER = "yes_other", "Ano, jiný formát"
        NO_NEED = "no_need", "Ne, potřebujeme navrhnout"
        NO_DONT_NEED = "no_dont_need", "Ne, nepotřebujeme"

    c_platform = ArrayField(
        models.CharField(max_length=30),
        default=list,
        blank=True,
        help_text="Multi-select: web, mobile_ios, mobile_android, desktop, api_only",
    )
    c_offline_mode = models.CharField(
        max_length=10, choices=OfflineMode.choices, blank=True
    )
    c_user_roles = ArrayField(
        models.CharField(max_length=40),
        default=list,
        blank=True,
        help_text="Multi-select: admin, manager, user, guest, api_client",
    )
    c_auth_methods = ArrayField(
        models.CharField(max_length=30),
        default=list,
        blank=True,
        help_text="Multi-select: email_password, social_login, sso, 2fa, api_key",
    )
    c_has_payments = models.CharField(
        max_length=5, choices=YesNo.choices, blank=True
    )
    c_payment_gateway = ArrayField(
        models.CharField(max_length=30),
        default=list,
        blank=True,
        help_text="Multi-select: stripe, gopay, comgate, paypal, bank_transfer",
    )
    c_multilingual = models.CharField(
        max_length=5, choices=YesNo.choices, blank=True
    )
    c_has_design = models.CharField(
        max_length=20, choices=HasDesign.choices, blank=True
    )
    c_key_features = models.TextField("Key features description", blank=True)
    c_existing_codebase = models.CharField(
        max_length=5, choices=YesNo.choices, blank=True
    )
    c_repo_access = models.CharField(
        max_length=5, choices=YesNo.choices, blank=True
    )

    # ── Section D: Web & e-shop (conditional: website_eshop in B1) ───

    class WebsiteType(models.TextChoices):
        PRESENTATION = "presentation", "Prezentační web"
        ESHOP = "eshop", "E-shop"
        CATALOG = "catalog", "Katalogový web"
        PORTAL = "portal", "Portál / platforma"
        LANDING = "landing", "Landing page"
        BLOG = "blog", "Blog / magazín"

    class ProductCount(models.TextChoices):
        UNDER_50 = "under_50", "Pod 50"
        R50_500 = "50_500", "50–500"
        R500_5000 = "500_5000", "500–5 000"
        OVER_5000 = "over_5000", "Nad 5 000"
        NA = "na", "Neaplikováno"

    class SEORequirements(models.TextChoices):
        BASIC = "basic", "Základní SEO"
        ADVANCED = "advanced", "Pokročilé SEO"
        NONE = "none", "Nepotřebujeme"

    class ContentManagement(models.TextChoices):
        WE_MANAGE = "we_manage", "Budeme spravovat sami"
        YOU_MANAGE = "you_manage", "Chceme správu od vás"
        BOTH = "both", "Kombinace"

    class PreferredCMS(models.TextChoices):
        WORDPRESS = "wordpress", "WordPress"
        SHOPIFY = "shopify", "Shopify"
        CUSTOM = "custom", "Na míru"
        NO_PREFERENCE = "no_preference", "Bez preference"
        OTHER = "other", "Jiné"

    d_website_type = models.CharField(
        max_length=20, choices=WebsiteType.choices, blank=True
    )
    d_product_count = models.CharField(
        max_length=20, choices=ProductCount.choices, blank=True
    )
    d_erp_connection = models.CharField(
        max_length=5, choices=YesNo.choices, blank=True
    )
    d_erp_system = models.TextField("ERP system details", blank=True)
    d_has_domain = models.CharField(
        max_length=5, choices=YesNo.choices, blank=True
    )
    d_has_hosting = models.CharField(
        max_length=5, choices=YesNo.choices, blank=True
    )
    d_seo_requirements = models.CharField(
        max_length=20, choices=SEORequirements.choices, blank=True
    )
    d_content_management = models.CharField(
        max_length=20, choices=ContentManagement.choices, blank=True
    )
    d_preferred_cms = models.CharField(
        max_length=20, choices=PreferredCMS.choices, blank=True
    )

    # ── Section E: AI & automation (conditional: ai_automation in B1) ─

    class DataVolume(models.TextChoices):
        SMALL = "small", "Malý (MB)"
        MEDIUM = "medium", "Střední (GB)"
        LARGE = "large", "Velký (TB+)"
        UNKNOWN = "unknown", "Nevím"

    class GDPRSensitivity(models.TextChoices):
        LOW = "low", "Nízká — veřejná data"
        MEDIUM = "medium", "Střední — interní data"
        HIGH = "high", "Vysoká — osobní údaje / GDPR"
        VERY_HIGH = "very_high", "Velmi vysoká — zdravotní / finanční"

    e_ai_solution_type = ArrayField(
        models.CharField(max_length=40),
        default=list,
        blank=True,
        help_text="Multi-select: chatbot, data_analysis, document_processing, "
        "recommendation, prediction, automation, image_recognition, other",
    )
    e_data_sources = ArrayField(
        models.CharField(max_length=40),
        default=list,
        blank=True,
        help_text="Multi-select: database, api, files, emails, web_scraping, iot, other",
    )
    e_data_volume = models.CharField(
        max_length=10, choices=DataVolume.choices, blank=True
    )
    e_local_ai_requirement = models.CharField(
        max_length=5, choices=YesNo.choices, blank=True
    )
    e_gdpr_sensitivity = models.CharField(
        max_length=20, choices=GDPRSensitivity.choices, blank=True
    )
    e_existing_automation = models.CharField(
        max_length=5, choices=YesNo.choices, blank=True
    )
    e_ai_language = ArrayField(
        models.CharField(max_length=20),
        default=list,
        blank=True,
        help_text="Multi-select: cs, en, de, sk, other",
    )

    # ── Section F: Enterprise system (conditional: enterprise_system in B1)

    class CustomVsReady(models.TextChoices):
        CUSTOM = "custom", "Na míru"
        READY = "ready", "Hotové řešení"
        HYBRID = "hybrid", "Kombinace"
        UNKNOWN = "unknown", "Nevím"

    class ConcurrentUsers(models.TextChoices):
        U1_10 = "1_10", "1–10"
        U11_50 = "11_50", "11–50"
        U51_200 = "51_200", "51–200"
        U200_PLUS = "200_plus", "200+"

    class DataMigration(models.TextChoices):
        YES = "yes", "Ano, z existujícího systému"
        PARTIAL = "partial", "Částečně"
        NO = "no", "Ne, začínáme na zelené louce"

    f_system_type = ArrayField(
        models.CharField(max_length=30),
        default=list,
        blank=True,
        help_text="Multi-select: crm, erp, hrm, dms, project_mgmt, "
        "accounting, warehouse, other",
    )
    f_current_system = models.TextField("Current system details", blank=True)
    f_dissatisfaction_reasons = ArrayField(
        models.CharField(max_length=40),
        default=list,
        blank=True,
        help_text="Multi-select: slow, expensive, missing_features, "
        "no_integration, outdated, no_support, other",
    )
    f_custom_vs_ready = models.CharField(
        max_length=10, choices=CustomVsReady.choices, blank=True
    )
    f_concurrent_users = models.CharField(
        max_length=10, choices=ConcurrentUsers.choices, blank=True
    )
    f_data_migration = models.CharField(
        max_length=10, choices=DataMigration.choices, blank=True
    )

    # ── Section G: Integration (conditional: integration in B1) ──────

    class IntegrationDirection(models.TextChoices):
        ONE_WAY = "one_way", "Jednosměrná"
        TWO_WAY = "two_way", "Obousměrná"
        BOTH = "both", "Obojí"

    class SyncFrequency(models.TextChoices):
        REALTIME = "realtime", "Real-time"
        HOURLY = "hourly", "Každou hodinu"
        DAILY = "daily", "Denně"
        ON_DEMAND = "on_demand", "Na vyžádání"

    g_systems_to_connect = ArrayField(
        models.CharField(max_length=40),
        default=list,
        blank=True,
        help_text="Multi-select: erp, crm, accounting, eshop, email, "
        "calendar, storage, custom_api, other",
    )
    g_systems_details = models.TextField("Integration details", blank=True)
    g_integration_direction = models.CharField(
        max_length=10, choices=IntegrationDirection.choices, blank=True
    )
    g_sync_frequency = models.CharField(
        max_length=10, choices=SyncFrequency.choices, blank=True
    )
    g_has_api_docs = models.CharField(
        max_length=5, choices=YesNo.choices, blank=True
    )

    # ── Section H: Security (conditional: security in B1) ────────────

    h_security_service_type = ArrayField(
        models.CharField(max_length=30),
        default=list,
        blank=True,
        help_text="Multi-select: audit, pentest, monitoring, "
        "incident_response, compliance, training",
    )
    h_had_incident = models.CharField(
        max_length=5, choices=YesNo.choices, blank=True
    )
    h_regulatory_requirements = ArrayField(
        models.CharField(max_length=30),
        default=list,
        blank=True,
        help_text="Multi-select: gdpr, iso27001, pci_dss, hipaa, sox, none",
    )

    # ── Section I: Data & analytics (conditional: data_analytics in B1)

    i_data_needs = ArrayField(
        models.CharField(max_length=30),
        default=list,
        blank=True,
        help_text="Multi-select: dashboards, reports, etl, "
        "data_warehouse, visualization, other",
    )
    i_data_sources = ArrayField(
        models.CharField(max_length=30),
        default=list,
        blank=True,
        help_text="Multi-select: database, spreadsheets, api, files, "
        "web_analytics, other",
    )
    i_existing_bi_tool = models.CharField(
        max_length=5, choices=YesNo.choices, blank=True
    )
    i_report_users = ArrayField(
        models.CharField(max_length=30),
        default=list,
        blank=True,
        help_text="Multi-select: management, analysts, all_employees, clients",
    )

    # ── Section J: Support & training (conditional: support/training) ─

    class RequiredSLA(models.TextChoices):
        BASIC = "basic", "Základní (next business day)"
        STANDARD = "standard", "Standardní (8h)"
        PREMIUM = "premium", "Premium (4h)"
        CRITICAL = "critical", "Kritický (1h)"

    class TrainingCount(models.TextChoices):
        UNDER_10 = "under_10", "Pod 10"
        R10_50 = "10_50", "10–50"
        R50_200 = "50_200", "50–200"
        OVER_200 = "over_200", "200+"

    class TrainingFormat(models.TextChoices):
        ONSITE = "onsite", "Prezenčně"
        ONLINE = "online", "Online"
        HYBRID = "hybrid", "Kombinace"
        SELF_PACED = "self_paced", "E-learning"

    j_support_type = ArrayField(
        models.CharField(max_length=30),
        default=list,
        blank=True,
        help_text="Multi-select: helpdesk, monitoring, maintenance, "
        "on_call, consulting",
    )
    j_required_sla = models.CharField(
        max_length=10, choices=RequiredSLA.choices, blank=True
    )
    j_training_type = ArrayField(
        models.CharField(max_length=30),
        default=list,
        blank=True,
        help_text="Multi-select: user_training, admin_training, "
        "technical_training, documentation",
    )
    j_training_count = models.CharField(
        max_length=10, choices=TrainingCount.choices, blank=True
    )
    j_training_format = models.CharField(
        max_length=10, choices=TrainingFormat.choices, blank=True
    )

    # ── Section K: Budget, timeline & priority (always visible) ──────

    class BudgetRange(models.TextChoices):
        UNDER_50K = "under_50k", "Pod 50 000 Kč"
        R50_100K = "50_100k", "50 000 – 100 000 Kč"
        R100_250K = "100_250k", "100 000 – 250 000 Kč"
        R250_500K = "250_500k", "250 000 – 500 000 Kč"
        R500K_1M = "500k_1m", "500 000 – 1 mil. Kč"
        R1M_3M = "1m_3m", "1 – 3 mil. Kč"
        OVER_3M = "over_3m", "Nad 3 mil. Kč"
        UNKNOWN = "unknown", "Nevím / řekněte vy"

    class PricingModel(models.TextChoices):
        FIXED = "fixed", "Pevná cena"
        TIME_MATERIAL = "time_material", "Time & Material"
        RETAINER = "retainer", "Retainer (měsíční paušál)"
        MILESTONE = "milestone", "Milestone-based"
        NO_PREFERENCE = "no_preference", "Bez preference"

    class LaunchDeadline(models.TextChoices):
        ASAP = "asap", "Co nejdříve"
        ONE_MONTH = "1month", "Do 1 měsíce"
        THREE_MONTHS = "3months", "Do 3 měsíců"
        SIX_MONTHS = "6months", "Do 6 měsíců"
        YEAR = "year", "Do roku"
        FLEXIBLE = "flexible", "Flexibilní"

    class PrefersModel(models.TextChoices):
        MVP = "mvp", "Ano, MVP nejdřív"
        FULL = "full", "Ne, chceme kompletní řešení"
        UNKNOWN = "unknown", "Nevím, poraďte"

    class Priority(models.TextChoices):
        SPEED = "speed", "Rychlost dodání"
        QUALITY = "quality", "Kvalita / stabilita"
        PRICE = "price", "Nízká cena"
        INNOVATION = "innovation", "Inovativnost"

    class DecisionMaker(models.TextChoices):
        CONTACT = "contact", "Kontaktní osoba"
        BOARD = "board", "Vedení / board"
        TEAM = "team", "Rozhoduje tým"

    class DecisionHorizon(models.TextChoices):
        IMMEDIATELY = "immediately", "Ihned"
        WEEKS = "weeks", "Během týdnů"
        MONTHS = "months", "Během měsíců"
        EXPLORING = "exploring", "Jen zjišťujeme"

    k_budget_range = models.CharField(
        max_length=20, choices=BudgetRange.choices, blank=True
    )
    k_pricing_model = models.CharField(
        max_length=20, choices=PricingModel.choices, blank=True
    )
    k_launch_deadline = models.CharField(
        max_length=10, choices=LaunchDeadline.choices, blank=True
    )
    k_specific_deadline = models.DateField(null=True, blank=True)
    k_prefers_mvp = models.CharField(
        max_length=10, choices=PrefersModel.choices, blank=True
    )
    k_priority = models.CharField(
        max_length=20, choices=Priority.choices, blank=True
    )
    k_decision_maker = models.CharField(
        max_length=10, choices=DecisionMaker.choices, blank=True
    )
    k_decision_horizon = models.CharField(
        max_length=20, choices=DecisionHorizon.choices, blank=True
    )

    # ── Section L: Technical preferences (conditional: budget >= 500k) ─

    class HostingPreference(models.TextChoices):
        CLOUD_CZ = "cloud_cz", "Cloud (české DC)"
        CLOUD_EU = "cloud_eu", "Cloud (EU)"
        CLOUD_GLOBAL = "cloud_global", "Cloud (globální)"
        ON_PREMISE = "on_premise", "On-premise"
        NO_PREFERENCE = "no_preference", "Bez preference"

    class DatabasePreference(models.TextChoices):
        POSTGRESQL = "postgresql", "PostgreSQL"
        MYSQL = "mysql", "MySQL"
        MSSQL = "mssql", "MS SQL"
        MONGODB = "mongodb", "MongoDB"
        NO_PREFERENCE = "no_preference", "Bez preference"

    class CodeOwnership(models.TextChoices):
        FULL = "full", "Plné vlastnictví kódu"
        LICENSE = "license", "Licence"
        NO_PREFERENCE = "no_preference", "Bez preference"

    l_has_it_team = models.CharField(
        max_length=5, choices=YesNo.choices, blank=True
    )
    l_preferred_stack = ArrayField(
        models.CharField(max_length=30),
        default=list,
        blank=True,
        help_text="Multi-select: python, javascript, typescript, java, "
        "dotnet, php, go, rust, no_preference",
    )
    l_hosting_preference = models.CharField(
        max_length=20, choices=HostingPreference.choices, blank=True
    )
    l_database_preference = models.CharField(
        max_length=20, choices=DatabasePreference.choices, blank=True
    )
    l_cicd_devops = models.CharField(
        max_length=5, choices=YesNo.choices, blank=True
    )
    l_code_ownership = models.CharField(
        max_length=20, choices=CodeOwnership.choices, blank=True
    )

    # ── Section M: Call conclusion (always visible) ──────────────────

    class LeadSource(models.TextChoices):
        REFERRAL = "referral", "Doporučení"
        GOOGLE = "google", "Google"
        SOCIAL = "social", "Sociální sítě"
        EVENT = "event", "Event / konference"
        COLD = "cold", "Cold outreach"
        RETURNING = "returning", "Vracející se klient"
        OTHER = "other", "Jiné"

    class NextStep(models.TextChoices):
        PROPOSAL = "proposal", "Zaslat nabídku"
        MEETING = "meeting", "Domluvit schůzku"
        DEMO = "demo", "Připravit demo"
        WAITING = "waiting", "Čeká na klienta"
        DECLINED = "declined", "Klient odmítl"

    class LeadRating(models.TextChoices):
        HOT = "hot", "Hot — uzavřeme brzy"
        WARM = "warm", "Warm — reálný zájem"
        COOL = "cool", "Cool — zvažuje"
        COLD = "cold", "Cold — jen zjišťuje"

    m_lead_source = models.CharField(
        max_length=20, choices=LeadSource.choices, blank=True
    )
    m_next_step = models.CharField(
        max_length=20, choices=NextStep.choices, blank=True
    )
    m_next_contact_date = models.DateField(null=True, blank=True)
    m_sales_notes = models.TextField("Sales notes", blank=True)
    m_lead_rating = models.CharField(
        max_length=10, choices=LeadRating.choices, blank=True
    )

    # ── AI fields ────────────────────────────────────────────────────

    ai_raw_text = models.TextField("AI raw text input", blank=True)
    ai_raw_file = models.FileField(
        upload_to="questionnaire_uploads/", blank=True
    )

    # ── Meta fields ──────────────────────────────────────────────────

    deal = models.OneToOneField(
        "pipeline.Deal",
        on_delete=models.CASCADE,
        related_name="questionnaire",
    )
    filled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="filled_questionnaires",
    )
    filled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "questionnaire response"

    def __str__(self) -> str:
        return f"Dotazník: {self.deal.client_company}"
