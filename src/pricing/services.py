from decimal import Decimal

from src.questionnaire.models import QuestionnaireResponse

from .models import PricingMatrix, PricingModifier

# Fallback values if database is empty
FALLBACK_CATEGORY_BASE_HOURS: dict[str, int] = {
    "custom_dev": 160,
    "website_eshop": 80,
    "ai_automation": 120,
    "enterprise_system": 200,
    "integration": 60,
    "security": 40,
    "data_analytics": 80,
    "support": 20,
    "training": 16,
    "mobile_app": 160,
    "cloud_migration": 80,
    "iot": 120,
    "blockchain": 160,
    "other": 80,
}

FALLBACK_USER_MULTIPLIER: dict[str, Decimal] = {
    "1_5": Decimal("1.0"),
    "6_20": Decimal("1.1"),
    "21_50": Decimal("1.2"),
    "51_200": Decimal("1.4"),
    "201_1000": Decimal("1.6"),
    "1001_plus": Decimal("1.8"),
    "public": Decimal("2.0"),
}

# Default deposit percentage
DEFAULT_DEPOSIT_PERCENT = Decimal("0.3")


def get_category_config(category: str) -> tuple[int, Decimal]:
    """Get base hours and rate for a category from database or fallback."""
    try:
        matrix = PricingMatrix.objects.filter(category=category, is_active=True).first()
        if matrix:
            return matrix.base_hours, matrix.hourly_rate
    except Exception:
        pass
    return FALLBACK_CATEGORY_BASE_HOURS.get(category, 80), Decimal("1500")


def get_modifier(modifier_type: str, key: str) -> tuple[Decimal, int]:
    """Get multiplier and extra hours for a modifier from database or fallback."""
    try:
        mod = PricingModifier.objects.filter(
            modifier_type=modifier_type, key=key, is_active=True
        ).first()
        if mod:
            return mod.multiplier, mod.extra_hours
    except Exception:
        pass
    # Fallback for user_count
    if modifier_type == "user_count":
        return FALLBACK_USER_MULTIPLIER.get(key, Decimal("1.2")), 0
    return Decimal("1.0"), 0


def calculate_proposal(questionnaire: QuestionnaireResponse) -> dict:
    """Auto-calculate pricing from new questionnaire fields.

    Uses PricingMatrix and PricingModifier from database when available,
    falls back to hardcoded values otherwise.

    Returns dict with: items, base_price, total_price, deposit_amount
    """
    items: list[dict] = []

    # 1. Sum base hours and weighted average rate from all selected categories
    categories = questionnaire.b_main_categories or []
    total_hours = 0
    total_weighted_rate = Decimal("0")

    for cat in categories:
        hours, rate = get_category_config(cat)
        total_hours += hours
        total_weighted_rate += rate * hours

    if not total_hours:
        total_hours = 80
        total_weighted_rate = Decimal("120000")  # 80 * 1500

    # Calculate weighted average rate
    avg_rate = total_weighted_rate / total_hours if total_hours > 0 else Decimal("1500")
    dev_hours = total_hours

    # 2. User count multiplier
    user_mult, _ = get_modifier("user_count", questionnaire.b_estimated_users)
    dev_hours = int(Decimal(str(dev_hours)) * user_mult)

    # 3. Platform extras (section C)
    platforms = questionnaire.c_platform or []
    for i, platform in enumerate(platforms):
        if i > 0:  # First platform is included in base
            _, extra_hours = get_modifier("platform", platform)
            dev_hours += extra_hours

    items.append({
        "name": "Vývoj",
        "hours": dev_hours,
        "rate": float(avg_rate),
        "total": float(Decimal(str(dev_hours)) * avg_rate),
    })

    # 4. Design (section C)
    _, design_hours = get_modifier("design", questionnaire.c_has_design)
    if design_hours > 0:
        items.append({
            "name": "Design",
            "hours": design_hours,
            "rate": float(avg_rate),
            "total": float(Decimal(str(design_hours)) * avg_rate),
        })

    # 5. Integration hours (section G)
    systems = questionnaire.g_systems_to_connect or []
    if systems:
        integration_hours = len(systems) * 16
        items.append({
            "name": "Integrace",
            "hours": integration_hours,
            "rate": float(avg_rate),
            "total": float(Decimal(str(integration_hours)) * avg_rate),
        })

    # 6. Security (section H)
    security_services = questionnaire.h_security_service_type or []
    if security_services:
        security_hours = len(security_services) * 12
        items.append({
            "name": "Bezpečnost",
            "hours": security_hours,
            "rate": float(avg_rate),
            "total": float(Decimal(str(security_hours)) * avg_rate),
        })

    # 7. Data migration (section F)
    if questionnaire.f_data_migration in ("yes", "partial"):
        migration_hours = 24 if questionnaire.f_data_migration == "yes" else 12
        items.append({
            "name": "Migrace dat",
            "hours": migration_hours,
            "rate": float(avg_rate),
            "total": float(Decimal(str(migration_hours)) * avg_rate),
        })

    # 8. Training (section J)
    training_types = questionnaire.j_training_type or []
    if training_types:
        training_hours = len(training_types) * 8
        items.append({
            "name": "Školení",
            "hours": training_hours,
            "rate": float(avg_rate),
            "total": float(Decimal(str(training_hours)) * avg_rate),
        })

    # 9. Support (section J)
    support_types = questionnaire.j_support_type or []
    if support_types:
        support_hours = len(support_types) * 8
        items.append({
            "name": "Podpora (měsíční)",
            "hours": support_hours,
            "rate": float(avg_rate),
            "total": float(Decimal(str(support_hours)) * avg_rate),
        })

    total = Decimal(str(sum(item["total"] for item in items)))
    deposit = total * DEFAULT_DEPOSIT_PERCENT

    return {
        "items": items,
        "base_price": float(total),
        "total_price": float(total),
        "deposit_amount": float(deposit),
    }
