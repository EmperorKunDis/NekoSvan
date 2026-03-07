"""Populate default pricing matrix data."""

from decimal import Decimal

from django.db import migrations


def populate_pricing_matrix(apps, schema_editor):
    PricingMatrix = apps.get_model("pricing", "PricingMatrix")
    PricingModifier = apps.get_model("pricing", "PricingModifier")

    # Categories with base hours
    categories = [
        ("custom_dev", "Vývoj na míru", 160, 1500),
        ("website_eshop", "Web & E-shop", 80, 1500),
        ("ai_automation", "AI & Automatizace", 120, 1800),
        ("enterprise_system", "Podnikový systém", 200, 1500),
        ("integration", "Integrace", 60, 1500),
        ("security", "Bezpečnost", 40, 1800),
        ("data_analytics", "Data & Analytika", 80, 1600),
        ("support", "Podpora", 20, 1200),
        ("training", "Školení", 16, 1200),
        ("mobile_app", "Mobilní aplikace", 160, 1600),
        ("cloud_migration", "Cloud migrace", 80, 1500),
        ("iot", "IoT", 120, 1700),
        ("blockchain", "Blockchain", 160, 2000),
        ("other", "Ostatní", 80, 1500),
    ]

    for cat, label, hours, rate in categories:
        PricingMatrix.objects.get_or_create(
            category=cat,
            defaults={
                "category_label": label,
                "base_hours": hours,
                "hourly_rate": Decimal(str(rate)),
            },
        )

    # User count modifiers
    user_modifiers = [
        ("1_5", "1–5 uživatelů", "1.0"),
        ("6_20", "6–20 uživatelů", "1.1"),
        ("21_50", "21–50 uživatelů", "1.2"),
        ("51_200", "51–200 uživatelů", "1.4"),
        ("201_1000", "201–1000 uživatelů", "1.6"),
        ("1001_plus", "1000+ uživatelů", "1.8"),
        ("public", "Veřejnost (neomezeno)", "2.0"),
    ]

    for key, label, mult in user_modifiers:
        PricingModifier.objects.get_or_create(
            modifier_type="user_count",
            key=key,
            defaults={
                "label": label,
                "multiplier": Decimal(mult),
            },
        )

    # Complexity modifiers
    complexity_modifiers = [
        ("low", "Nízká", "1.0"),
        ("medium", "Střední", "1.3"),
        ("high", "Vysoká", "1.6"),
        ("very_high", "Velmi vysoká", "2.0"),
    ]

    for key, label, mult in complexity_modifiers:
        PricingModifier.objects.get_or_create(
            modifier_type="complexity",
            key=key,
            defaults={
                "label": label,
                "multiplier": Decimal(mult),
            },
        )

    # Design modifiers (extra hours instead of multiplier)
    design_modifiers = [
        ("yes_figma", "Ano, v Figmě", 0),
        ("yes_other", "Ano, jiný formát", 10),
        ("no_need", "Ne, potřebujeme navrhnout", 40),
        ("no_dont_need", "Ne, nepotřebujeme", 0),
    ]

    for key, label, hours in design_modifiers:
        PricingModifier.objects.get_or_create(
            modifier_type="design",
            key=key,
            defaults={
                "label": label,
                "multiplier": Decimal("1.0"),
                "extra_hours": hours,
            },
        )

    # Platform modifiers (extra hours per additional platform)
    platform_modifiers = [
        ("web", "Web", 0),
        ("mobile_ios", "iOS", 40),
        ("mobile_android", "Android", 40),
        ("desktop", "Desktop", 60),
        ("api_only", "API only", 20),
    ]

    for key, label, hours in platform_modifiers:
        PricingModifier.objects.get_or_create(
            modifier_type="platform",
            key=key,
            defaults={
                "label": label,
                "multiplier": Decimal("1.0"),
                "extra_hours": hours,
            },
        )


def reverse_populate(apps, schema_editor):
    PricingMatrix = apps.get_model("pricing", "PricingMatrix")
    PricingModifier = apps.get_model("pricing", "PricingModifier")
    PricingMatrix.objects.all().delete()
    PricingModifier.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("pricing", "0002_add_pricing_matrix"),
    ]

    operations = [
        migrations.RunPython(populate_pricing_matrix, reverse_populate),
    ]
