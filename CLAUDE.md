# NekoSvan Workflow System

## Projekt
Automatizovaný systém workflow pro ADNP × NekoSvan × Praut. IT služby, 15+ zakázek/měsíc.
Deal prochází 8 fázemi: lead → qualification → pricing → presentation → contract → planning → development → completed.

## Stack
- **Backend:** Django 6.0 + DRF, PostgreSQL, Celery + Redis, WeasyPrint
- **Frontend:** Angular (v `frontend/`)
- **Automatizace:** N8N webhooks
- **DB:** `nekosvan`, user `martinsvanda`, localhost:5432
- **Settings:** `config.settings.local` (dev), `config.settings.production` (prod)

## Příkazy
```bash
source venv/bin/activate
python manage.py runserver          # Dev server
python manage.py check              # System check
ruff check src/ config/             # Linting
pytest src/ -v                      # Testy
python manage.py makemigrations     # Nové migrace
python manage.py migrate            # Aplikovat migrace
celery -A config worker -l info     # Celery worker
```

## Struktura
```
src/
├── accounts/     # User (AbstractUser), Company, role-based access
├── pipeline/     # Deal (8 fází), DealActivity, auto-assignment
├── questionnaire/# QuestionnaireResponse (1:1 Deal)
├── pricing/      # Proposal, auto-kalkulace z cenové matice
├── contracts/    # Contract, ContractTemplate, Payment, PDF gen
├── projects/     # Project, Milestone, ProjectComment, QA workflow
├── notifications/# Notification, N8N webhook triggers
└── client_portal/# Token-based public API (UUID v URL)
config/
├── settings/     # base.py, local.py, production.py
├── celery.py     # Celery config
└── urls.py       # Root URL config
frontend/         # Angular SPA
```

## API
- `/api/v1/{app}/` — authenticated DRF endpoints
- `/portal/{token}/` — public client portal (no auth, UUID token)
- `/admin/` — Django admin

## Konvence
- Kód a komentáře anglicky, komunikace česky
- Soubory max 300 řádků
- Ruff pro formátování (NE black/flake8)
- Pojmenované migrace
- Testy: pytest + pytest-django
- Services pattern: business logika v `services.py`, ne ve views

## Role
- `adam` — ADNP, akvizice + smlouvy
- `vadim` — kvalifikace + prezentace klientům
- `martin` — Praut, cenotvorba + vývoj
- `nekosvan` — QA review + oversight
- `client` — klientský portál
