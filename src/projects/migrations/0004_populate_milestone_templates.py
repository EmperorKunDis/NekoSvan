"""Populate default milestone templates."""

from django.db import migrations


TEMPLATES = {
    "custom_dev": {
        "name": "Vývoj na míru — Standardní",
        "items": [
            ("Architektura a prototyp", "Návrh architektury, základní prototyp", 24),
            ("Core funkce", "Implementace klíčových funkcí", 48),
            ("API a integrace", "API endpointy, integrace třetích stran", 32),
            ("UI/UX polish", "Finální UI, UX vylepšení", 24),
            ("Testování a QA", "Unit testy, E2E testy, security audit", 24),
            ("Deploy a předání", "Nasazení, dokumentace, školení", 16),
        ],
    },
    "website_eshop": {
        "name": "Web & E-shop — Standardní",
        "items": [
            ("Wireframy a design", "Návrh struktury a vizuálu", 16),
            ("Frontend implementace", "HTML/CSS, responzivita", 24),
            ("Backend a CMS", "Backend logika, správa obsahu", 24),
            ("Testování a QA", "Cross-browser, výkon, bezpečnost", 12),
            ("Deploy a předání", "Nasazení na produkci", 8),
        ],
    },
    "ai_automation": {
        "name": "AI & Automatizace — Standardní",
        "items": [
            ("Analýza a PoC", "Analýza dat, proof of concept", 24),
            ("Model a pipeline", "Implementace AI modelu/pipeline", 40),
            ("Integrace", "Napojení na existující systémy", 24),
            ("Testování a optimalizace", "Výkon, přesnost, edge cases", 24),
            ("Deploy a monitoring", "Nasazení, monitoring, alerting", 16),
        ],
    },
    "enterprise_system": {
        "name": "Podnikový systém — Standardní",
        "items": [
            ("Analýza požadavků", "Detailní analýza business procesů", 32),
            ("Architektura a prototyp", "Systémový design, prototyp", 40),
            ("Core implementace", "Hlavní moduly a funkce", 64),
            ("Integrace a migrace dat", "Napojení na systémy, migrace", 40),
            ("UAT a školení", "Akceptační testy, školení uživatelů", 24),
            ("Deploy a předání", "Nasazení, dokumentace", 16),
        ],
    },
    "integration": {
        "name": "Integrace — Standardní",
        "items": [
            ("Analýza a mapování API", "Analýza API, dokumentace endpointů", 16),
            ("Implementace integrace", "Vývoj integračních konektorů", 24),
            ("Testování a validace", "Testování všech scénářů", 16),
            ("Deploy a předání", "Nasazení, monitoring", 8),
        ],
    },
    "mobile_app": {
        "name": "Mobilní aplikace — Standardní",
        "items": [
            ("Návrh a prototyp", "UX/UI design, interaktivní prototyp", 24),
            ("Core vývoj", "Hlavní funkce aplikace", 48),
            ("Backend a API", "Backend služby, API", 32),
            ("Testování", "Unit testy, device testing", 24),
            ("App Store submission", "Příprava a publikace", 16),
            ("Post-launch podpora", "Bug fixes, optimalizace", 16),
        ],
    },
}


def populate_templates(apps, schema_editor):
    MilestoneTemplate = apps.get_model("projects", "MilestoneTemplate")
    MilestoneTemplateItem = apps.get_model("projects", "MilestoneTemplateItem")

    for category, data in TEMPLATES.items():
        template, created = MilestoneTemplate.objects.get_or_create(
            category=category,
            is_default=True,
            defaults={"name": data["name"]},
        )

        if created:
            for i, (title, desc, hours) in enumerate(data["items"]):
                MilestoneTemplateItem.objects.create(
                    template=template,
                    title=title,
                    description=desc,
                    order=i + 1,
                    estimated_hours=hours,
                )


def reverse_populate(apps, schema_editor):
    MilestoneTemplate = apps.get_model("projects", "MilestoneTemplate")
    MilestoneTemplate.objects.filter(is_default=True).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0003_add_milestone_templates"),
    ]

    operations = [
        migrations.RunPython(populate_templates, reverse_populate),
    ]
