from rest_framework import serializers

from .models import QuestionnaireResponse

# Valid values for ArrayField multi-select fields
VALID_CURRENT_IT = {
    "website", "eshop", "crm", "erp", "accounting",
    "project_mgmt", "custom_app", "ai_tools", "none",
}
VALID_MAIN_CATEGORIES = {
    "custom_dev", "website_eshop", "ai_automation", "enterprise_system",
    "integration", "security", "data_analytics", "support", "training",
    "mobile_app", "cloud_migration", "iot", "blockchain", "other",
}
VALID_TARGET_USERS = {"employees", "management", "clients", "partners", "public"}
VALID_PLATFORM = {"web", "mobile_ios", "mobile_android", "desktop", "api_only"}
VALID_USER_ROLES = {"admin", "manager", "user", "guest", "api_client"}
VALID_AUTH_METHODS = {"email_password", "social_login", "sso", "2fa", "api_key"}
VALID_PAYMENT_GATEWAY = {"stripe", "gopay", "comgate", "paypal", "bank_transfer"}
VALID_AI_SOLUTION = {
    "chatbot", "data_analysis", "document_processing", "recommendation",
    "prediction", "automation", "image_recognition", "other",
}
VALID_E_DATA_SOURCES = {
    "database", "api", "files", "emails", "web_scraping", "iot", "other",
}
VALID_AI_LANGUAGE = {"cs", "en", "de", "sk", "other"}
VALID_SYSTEM_TYPE = {
    "crm", "erp", "hrm", "dms", "project_mgmt",
    "accounting", "warehouse", "other",
}
VALID_DISSATISFACTION = {
    "slow", "expensive", "missing_features", "no_integration",
    "outdated", "no_support", "other",
}
VALID_SYSTEMS_TO_CONNECT = {
    "erp", "crm", "accounting", "eshop", "email",
    "calendar", "storage", "custom_api", "other",
}
VALID_SECURITY_SERVICE = {
    "audit", "pentest", "monitoring", "incident_response",
    "compliance", "training",
}
VALID_REGULATORY = {"gdpr", "iso27001", "pci_dss", "hipaa", "sox", "none"}
VALID_DATA_NEEDS = {
    "dashboards", "reports", "etl", "data_warehouse", "visualization", "other",
}
VALID_I_DATA_SOURCES = {
    "database", "spreadsheets", "api", "files", "web_analytics", "other",
}
VALID_REPORT_USERS = {"management", "analysts", "all_employees", "clients"}
VALID_SUPPORT_TYPE = {
    "helpdesk", "monitoring", "maintenance", "on_call", "consulting",
}
VALID_TRAINING_TYPE = {
    "user_training", "admin_training", "technical_training", "documentation",
}
VALID_PREFERRED_STACK = {
    "python", "javascript", "typescript", "java", "dotnet",
    "php", "go", "rust", "no_preference",
}

# Mapping: field name -> valid values set
ARRAY_FIELD_VALIDATORS: dict[str, set[str]] = {
    "a_current_it": VALID_CURRENT_IT,
    "b_main_categories": VALID_MAIN_CATEGORIES,
    "b_target_users": VALID_TARGET_USERS,
    "c_platform": VALID_PLATFORM,
    "c_user_roles": VALID_USER_ROLES,
    "c_auth_methods": VALID_AUTH_METHODS,
    "c_payment_gateway": VALID_PAYMENT_GATEWAY,
    "e_ai_solution_type": VALID_AI_SOLUTION,
    "e_data_sources": VALID_E_DATA_SOURCES,
    "e_ai_language": VALID_AI_LANGUAGE,
    "f_system_type": VALID_SYSTEM_TYPE,
    "f_dissatisfaction_reasons": VALID_DISSATISFACTION,
    "g_systems_to_connect": VALID_SYSTEMS_TO_CONNECT,
    "h_security_service_type": VALID_SECURITY_SERVICE,
    "h_regulatory_requirements": VALID_REGULATORY,
    "i_data_needs": VALID_DATA_NEEDS,
    "i_data_sources": VALID_I_DATA_SOURCES,
    "i_report_users": VALID_REPORT_USERS,
    "j_support_type": VALID_SUPPORT_TYPE,
    "j_training_type": VALID_TRAINING_TYPE,
    "l_preferred_stack": VALID_PREFERRED_STACK,
}


class QuestionnaireResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionnaireResponse
        fields = "__all__"
        read_only_fields = ("id", "filled_by", "filled_at")

    def validate(self, attrs: dict) -> dict:
        """Validate ArrayField values against allowed choices."""
        for field_name, valid_values in ARRAY_FIELD_VALIDATORS.items():
            values = attrs.get(field_name, [])
            if values:
                invalid = set(values) - valid_values
                if invalid:
                    raise serializers.ValidationError(
                        {field_name: f"Invalid values: {', '.join(sorted(invalid))}"}
                    )
        return attrs


class AIExtractSerializer(serializers.Serializer):
    text = serializers.CharField(required=False, allow_blank=True)
    file = serializers.FileField(required=False)

    def validate(self, attrs: dict) -> dict:
        if not attrs.get("text") and not attrs.get("file"):
            raise serializers.ValidationError(
                "Either 'text' or 'file' must be provided."
            )
        return attrs
