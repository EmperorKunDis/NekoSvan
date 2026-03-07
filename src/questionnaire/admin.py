from django.contrib import admin

from .models import QuestionnaireResponse


@admin.register(QuestionnaireResponse)
class QuestionnaireResponseAdmin(admin.ModelAdmin):
    list_display = (
        "deal",
        "a_company_name",
        "b_primary_goal",
        "k_budget_range",
        "m_lead_rating",
        "filled_at",
    )
    list_filter = (
        "a_industry",
        "b_primary_goal",
        "k_budget_range",
        "m_lead_rating",
        "m_next_step",
    )
    readonly_fields = ("filled_at",)
    search_fields = ("a_company_name", "a_ico", "a_contact_person", "a_email")

    fieldsets = (
        ("A — Klient & kontext", {
            "fields": (
                "a_company_name", "a_ico", "a_contact_person", "a_email",
                "a_phone", "a_industry", "a_industry_other",
                "a_employee_count", "a_annual_revenue",
                "a_current_it", "a_it_satisfaction",
            ),
        }),
        ("B — Typ projektu", {
            "fields": (
                "b_main_categories", "b_primary_goal",
                "b_target_users", "b_estimated_users",
            ),
        }),
        ("C — Vývoj na míru", {
            "classes": ("collapse",),
            "fields": (
                "c_platform", "c_offline_mode", "c_user_roles",
                "c_auth_methods", "c_has_payments", "c_payment_gateway",
                "c_multilingual", "c_has_design", "c_key_features",
                "c_existing_codebase", "c_repo_access",
            ),
        }),
        ("D — Web & e-shop", {
            "classes": ("collapse",),
            "fields": (
                "d_website_type", "d_product_count", "d_erp_connection",
                "d_erp_system", "d_has_domain", "d_has_hosting",
                "d_seo_requirements", "d_content_management", "d_preferred_cms",
            ),
        }),
        ("E — AI & automatizace", {
            "classes": ("collapse",),
            "fields": (
                "e_ai_solution_type", "e_data_sources", "e_data_volume",
                "e_local_ai_requirement", "e_gdpr_sensitivity",
                "e_existing_automation", "e_ai_language",
            ),
        }),
        ("F — Podnikový systém", {
            "classes": ("collapse",),
            "fields": (
                "f_system_type", "f_current_system",
                "f_dissatisfaction_reasons", "f_custom_vs_ready",
                "f_concurrent_users", "f_data_migration",
            ),
        }),
        ("G — Integrace", {
            "classes": ("collapse",),
            "fields": (
                "g_systems_to_connect", "g_systems_details",
                "g_integration_direction", "g_sync_frequency", "g_has_api_docs",
            ),
        }),
        ("H — Bezpečnost", {
            "classes": ("collapse",),
            "fields": (
                "h_security_service_type", "h_had_incident",
                "h_regulatory_requirements",
            ),
        }),
        ("I — Data & analytika", {
            "classes": ("collapse",),
            "fields": (
                "i_data_needs", "i_data_sources",
                "i_existing_bi_tool", "i_report_users",
            ),
        }),
        ("J — Podpora & školení", {
            "classes": ("collapse",),
            "fields": (
                "j_support_type", "j_required_sla",
                "j_training_type", "j_training_count", "j_training_format",
            ),
        }),
        ("K — Rozpočet & čas", {
            "fields": (
                "k_budget_range", "k_pricing_model", "k_launch_deadline",
                "k_specific_deadline", "k_prefers_mvp", "k_priority",
                "k_decision_maker", "k_decision_horizon",
            ),
        }),
        ("L — Technické preference", {
            "classes": ("collapse",),
            "fields": (
                "l_has_it_team", "l_preferred_stack",
                "l_hosting_preference", "l_database_preference",
                "l_cicd_devops", "l_code_ownership",
            ),
        }),
        ("M — Závěr hovoru", {
            "fields": (
                "m_lead_source", "m_next_step", "m_next_contact_date",
                "m_sales_notes", "m_lead_rating",
            ),
        }),
        ("AI", {
            "classes": ("collapse",),
            "fields": ("ai_raw_text", "ai_raw_file"),
        }),
        ("Meta", {
            "fields": ("deal", "filled_by", "filled_at"),
        }),
    )
