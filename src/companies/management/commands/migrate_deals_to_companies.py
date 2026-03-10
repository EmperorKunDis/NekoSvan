"""
Management command pro migraci existujících dealů do Company modelu.

Logika:
1. Projde všechny dealy které mají client_name ale nemají company FK
2. Pro každý deal:
   a) Zkusí najít existující Company podle IČO (pokud existuje)
   b) Pokud nenajde, vytvoří novou Company
   c) Propojí deal s company
3. Podporuje --dry-run pro test bez změn
4. Loguje vše co dělá
"""

from django.core.management.base import BaseCommand

from src.companies.models import Company
from src.pipeline.models import Deal


class Command(BaseCommand):
    help = "Migrate existing deals to Company model"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Run without making changes")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        # Najdi dealy bez company
        deals = Deal.objects.filter(company__isnull=True).exclude(client_name="")

        self.stdout.write(f"Found {deals.count()} deals to migrate")

        created = 0
        linked = 0

        for deal in deals:
            company = None

            # Zkus najít podle IČO
            if deal.client_ico:
                company = Company.objects.filter(ico=deal.client_ico).first()
                if company:
                    self.stdout.write(f"  Found existing company by ICO: {company.name}")

            # Zkus najít podle názvu
            if not company and deal.client_name:
                company = Company.objects.filter(name__iexact=deal.client_name).first()
                if company:
                    self.stdout.write(f"  Found existing company by name: {company.name}")

            # Vytvoř novou company
            if not company:
                if not dry_run:
                    company = Company.objects.create(
                        name=deal.client_name or f"Unknown (Deal #{deal.id})",
                        ico=deal.client_ico or "",
                        email=deal.client_email or "",
                        phone=deal.client_phone or "",
                        address=deal.client_address or "",
                        status="active" if deal.phase not in ["lead", "archived"] else "lead",
                    )
                created += 1
                self.stdout.write(f"  Created new company: {deal.client_name}")

            # Propoj deal s company
            if not dry_run and company:
                deal.company = company
                deal.save(update_fields=["company"])
            linked += 1

            self.stdout.write(f"  Linked deal #{deal.id} '{deal.title}' → {deal.client_name}")

        mode = "(DRY RUN)" if dry_run else ""
        self.stdout.write(
            self.style.SUCCESS(f"\n{mode} Migration complete: {created} companies created, {linked} deals linked")
        )
