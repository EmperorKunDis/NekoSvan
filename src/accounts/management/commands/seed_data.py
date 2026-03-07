"""Seed initial data: companies, users, contract templates."""

from django.core.management.base import BaseCommand

from src.accounts.models import Company, User
from src.contracts.models import ContractTemplate


class Command(BaseCommand):
    help = "Seed database with initial companies, users, and contract templates"

    def handle(self, *args, **options):
        self._create_companies()
        self._create_users()
        self._create_contract_templates()
        self.stdout.write(self.style.SUCCESS("Seed data created successfully."))

    def _create_companies(self):
        for name in Company.CompanyName.values:
            Company.objects.get_or_create(name=name)
            self.stdout.write(f"  Company: {name}")

    def _create_users(self):
        users = [
            {
                "username": "adam",
                "email": "adam@adnp.cz",
                "first_name": "Adam",
                "last_name": "ADNP",
                "role": User.Role.ADAM,
                "company_name": Company.CompanyName.ADNP,
            },
            {
                "username": "vadim",
                "email": "vadim@example.com",
                "first_name": "Vadim",
                "last_name": "",
                "role": User.Role.VADIM,
                "company_name": None,
            },
            {
                "username": "martin",
                "email": "martin@praut.cz",
                "first_name": "Martin",
                "last_name": "Praut",
                "role": User.Role.MARTIN,
                "company_name": Company.CompanyName.PRAUT,
            },
            {
                "username": "nekosvan",
                "email": "info@nekosvan.cz",
                "first_name": "NekoSvan",
                "last_name": "",
                "role": User.Role.NEKOSVAN,
                "company_name": Company.CompanyName.NEKOSVAN,
            },
        ]

        for u in users:
            company = None
            if u["company_name"]:
                company = Company.objects.get(name=u["company_name"])

            user, created = User.objects.get_or_create(
                username=u["username"],
                defaults={
                    "email": u["email"],
                    "first_name": u["first_name"],
                    "last_name": u["last_name"],
                    "role": u["role"],
                    "company": company,
                },
            )
            if created:
                user.set_password("changeme123")
                user.save()
                self.stdout.write(f"  User: {u['username']} ({u['role']})")
            else:
                self.stdout.write(f"  User: {u['username']} (already exists)")

    def _create_contract_templates(self):
        templates = [
            {
                "name": "Standardní smlouva o dílo",
                "body_template": """SMLOUVA O DÍLO

Objednatel: {{client_name}}
IČO: {{client_ico}}
Email: {{client_email}}

Zhotovitel: {{company_name}}

Předmět díla:
{{project_description}}

Celková cena: {{total_price}} Kč bez DPH
Záloha: {{deposit_amount}} Kč (splatná do 14 dnů od podpisu)
Doplatek: {{remaining_amount}} Kč (splatný po předání díla)

Termín dokončení: {{estimated_end_date}}

Podpis objednatele: _______________
Podpis zhotovitele: _______________
Datum: {{date}}
""",
            },
            {
                "name": "Smlouva s milníkovými platbami",
                "body_template": """SMLOUVA O DÍLO — MILNÍKOVÉ PLATBY

Objednatel: {{client_name}}
Zhotovitel: {{company_name}}

Předmět díla: {{project_description}}

Celková cena: {{total_price}} Kč bez DPH

Platební podmínky:
1. Záloha {{deposit_amount}} Kč — splatná do 14 dnů od podpisu
2. Průběžné platby dle milníků
3. Doplatek {{remaining_amount}} Kč — po předání díla

Podpis objednatele: _______________
Podpis zhotovitele: _______________
Datum: {{date}}
""",
            },
        ]

        for t in templates:
            _, created = ContractTemplate.objects.get_or_create(
                name=t["name"],
                defaults={"body_template": t["body_template"]},
            )
            status = "created" if created else "already exists"
            self.stdout.write(f"  Template: {t['name']} ({status})")
