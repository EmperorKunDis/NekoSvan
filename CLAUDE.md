# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Automated workflow system for ADNP × NekoSvan × Praut. IT services, 15+ deals/month.
Each Deal flows through 8 phases: lead → qualification → pricing → presentation → contract → planning → development → completed.

## Commands

```bash
source venv/bin/activate

# Backend
python manage.py runserver 13666                    # Dev server (port 13666)
python manage.py check                              # System check
ruff check src/ config/                             # Lint (NOT black/flake8)
pytest src/ -v                                      # All tests
pytest src/pipeline/tests/ -v                       # Single app tests
pytest src/pipeline/tests/test_services.py::TestPhaseTransitions::test_advance_from_lead_assigns_vadim -v  # Single test
python manage.py makemigrations --name descriptive_name  # Named migrations
python manage.py migrate
celery -A config worker -l info                     # Celery worker

# Frontend
cd frontend
npm install
ng serve --port 12666 --proxy-config proxy.conf.json  # Dev server (port 12666)
ng build                                              # Production build
```

Settings: `config.settings.local` (dev, default in manage.py), `config.settings.production` (prod/Docker).

## Architecture

### Deal-Centric Model Graph

Everything revolves around `Deal` (pipeline app). Most relationships are OneToOne:

```
Deal (pipeline)
├── ClientCompany             FK, nullable (pipeline) — structured client data (preferred)
│   (flat client_* fields)    — deprecated fallback, still writable
├── QuestionnaireResponse     1:1 (questionnaire)
├── Proposal(s)               FK, many (pricing) — auto-calculated from questionnaire
├── Contract                  1:1 (contracts) — PDF via WeasyPrint
│   └── Payment(s)            FK via Deal (contracts)
├── Project                   1:1 (projects) — auto-created on PLANNING phase
│   ├── Milestone(s)          FK — QA review workflow
│   └── QAChecklist           1:1
├── Document(s)               FK (documents) — ONLYOFFICE integration (JWT optional)
├── DealActivity(s)           FK — audit log (incl. portal access logs)
└── Notification(s)           FK
```

**Client data**: `Deal.get_client_data()` returns data from FK `ClientCompany` if set, otherwise from flat `client_*` fields. The `Company` model (accounts) represents only internal companies (ADNP, NekoSvan, Praut).

### Phase Transitions, Signals & Validators

Defined in `src/pipeline/services.py` — `advance_phase()` is the core function. Uses semantic role constants (`ROLE_SALES`, `ROLE_PRICING`, `ROLE_CONTRACTS`, `ROLE_PROJECT_MANAGEMENT`, `ROLE_QA`):

| From → To | Assigned Role | Side Effects (via signals) |
|-----------|---------------|----------------------------|
| lead → qualification | ROLE_SALES (Vadim) | Notification + N8N webhook |
| qualification → pricing | ROLE_PRICING (Martin) | |
| pricing → presentation | ROLE_SALES (Vadim) | |
| presentation → contract | ROLE_CONTRACTS (Adam) | |
| contract → planning | ROLE_PROJECT_MANAGEMENT (Martin) | **Auto-creates Project** (signal receiver) |
| planning → development | ROLE_PROJECT_MANAGEMENT (Martin) | |
| development → completed | ROLE_QA (NekoSvan) | |

**Signals** (`src/pipeline/signals.py`): `deal_phase_changed`, `deal_revision_requested`, `deal_archived`. Receivers registered in `projects.apps.ready()` and `notifications.apps.ready()` — this replaces lazy imports.

**Validators** (`src/pipeline/validators.py`): `validate_transition(deal, next_phase)` checks prerequisites (questionnaire for PRICING, proposal for PRESENTATION, accepted proposal for CONTRACT, signed contract for PLANNING, approved milestones for COMPLETED). Raises `PhaseTransitionError(message, phase, missing)`. Default `validate=True` in `advance_phase()`, pass `validate=False` for backward compat in tests.

`request_revision()` can only go presentation → pricing. After 3 revisions, deal auto-archives.

### Services Pattern

**All business logic lives in `services.py` files, never in views.** Key service modules:
- `pipeline.services` — phase transitions, auto-assignment (emits signals)
- `pipeline.validators` — per-phase prerequisite checks
- `pricing.services` — `calculate_proposal()` from questionnaire + PricingMatrix/PricingModifier DB tables
- `contracts.services` — contract generation, WeasyPrint PDF rendering
- `projects.services` — project/milestone creation, QA workflow
- `notifications.services` — dual channel: in-app DB records + async N8N Celery task
- `client_portal.services` — portal access logging (IP, user-agent → DealActivity)
- `questionnaire.services` — Ollama AI extraction (llama3.1) for parsing documents
- `documents.jwt_utils` — ONLYOFFICE JWT token generation/verification (HS256)

### Client Portal

UUID token in URL path with **expiration** and **rate limiting**:
- `Deal.portal_token` — auto-generated UUID, unique
- `Deal.portal_token_expires_at` — 90 days for new/active deals, 30 days for archived
- `Deal.is_portal_token_valid()` — checks expiration (None = always valid for backward compat)
- `Deal.refresh_portal_token(days=90)` — new UUID + fresh expiration
- `POST /deals/{id}/refresh-portal-token/` — endpoint to regenerate
- Throttled: `PortalReadThrottle` (30/min) on reads, `PortalWriteThrottle` (10/min) on writes
- All portal access logged via `log_portal_access()` → DealActivity with `portal:{action}`, IP, user-agent

### Role-Based Permissions

Semantic permission classes in `src/accounts/permissions.py` (preferred):
- `IsContractManager` → Adam
- `IsSalesLead` → Vadim
- `IsProjectManager` → Martin
- `IsQAReviewer` → Martin + NekoSvan

Old name-based classes (`IsAdam`, `IsVadim`, `IsMartin`, `IsNekoSvan`) still work but emit `DeprecationWarning`.

Generic: `IsInternalUser`, `DealPhasePermission`, `IsMartinRole` (Martin writes, others read-only), `IsQARole`.

User roles: `adam`, `vadim`, `martin`, `nekosvan`, `client`. The `is_master` flag allows creating sub-users of the same role.

### Notifications: Dual Channel + SSE

`notifications/services.py` creates both:
1. In-app `Notification` DB records (shown in Angular UI)
2. **Async** N8N webhook via Celery task `send_n8n_webhook` with **circuit breaker** (5 failures → 5min open, state in Redis cache)

**SSE endpoint**: `GET /api/v1/notifications/stream/` — `StreamingHttpResponse`, polls DB every 5s, sends heartbeat. Frontend uses `EventSource` with auto-reconnect (30s fallback).

### Celery Tasks

All tasks use `bind=True`, `autoretry_for=(Exception,)`, exponential backoff (60s→600s), `max_retries=3`, `soft_time_limit=120`, `time_limit=180`, `acks_late=True`:

- `pipeline.tasks.check_inactive_deals` — hourly, flags deals idle 48h+
- `contracts.tasks.check_overdue_payments` — hourly, marks overdue payments
- `contracts.tasks.generate_contract_pdf_task` — on-demand async PDF (skips retry on Deal.DoesNotExist)
- `notifications.tasks.send_n8n_webhook` — async webhook with circuit breaker (5 retries, 30s backoff)

### Health Check

`GET /health/` (no auth) — checks DB, Redis, Celery (critical), Ollama, ONLYOFFICE (optional). Returns `{"status": "healthy"|"degraded", "checks": {...}}` with 200 or 503. Docker healthcheck configured on backend container.

## Frontend (Angular)

- **Standalone components** throughout (no NgModules)
- **Lazy-loaded routes** via `loadComponent()` in `app.routes.ts`
- **Auth**: session-based with Django cookies; `AuthService` uses Angular Signals
- **Interceptors**: `csrfInterceptor` (CSRF token), `errorInterceptor` (401→login redirect, 403→toast, 429→warning, 500+→error). Portal URLs excluded from error interceptor
- **ToastService**: signal-based (`success`/`error`/`warning`/`info`), auto-dismiss (errors require manual dismiss)
- **NotificationService**: SSE via `EventSource` with auto-reconnect, signal-based `unreadCount`
- **API**: generic `ApiService` wraps `HttpClient` for `/api/v1/` calls; `DealService` adds typed deal methods
- **Proxy**: `proxy.conf.json` forwards `/api`, `/admin`, `/media` to `localhost:13666`

## Stack

- **Backend**: Django 6.0, DRF, PostgreSQL 16, Celery + Redis, WeasyPrint (PDF), drf-spectacular (OpenAPI)
- **Frontend**: Angular 21, standalone components, Tailwind-style with Praut branding (`#7c3aed` purple, `#06b6d4` cyan)
- **Docs**: ONLYOFFICE Document Server (JWT configurable via `ONLYOFFICE_JWT_SECRET`, port 9980)
- **AI**: Ollama (llama3.1) for questionnaire extraction
- **Automation**: N8N webhooks (async via Celery)
- **Cache**: Redis (reuses Celery broker URL)
- **DB**: `nekosvan`, user `martinsvanda`, localhost:5432

## API Endpoints

- `/api/v1/{app}/` — authenticated DRF endpoints (session auth)
- `/portal/{token}/` — public client portal (UUID token, no auth, rate-limited)
- `/api/v1/notifications/stream/` — SSE notifications (authenticated)
- `/health/` — health check (no auth)
- `/api/docs/` — Swagger UI (drf-spectacular)
- `/admin/` — Django admin

## Conventions

- Code and comments in English, communication in Czech
- Files max 300 lines
- Ruff for linting (`line-length = 120`, rules: E, F, I, N, W; E501 ignored)
- Named migrations (`--name descriptive_name`)
- Tests: pytest + pytest-django, `factory_boy` factories in `tests/factories.py`, shared fixtures in root `conftest.py`
- Services pattern: business logic in `services.py`, never in views
- Signals for cross-app communication (replaces lazy imports)
- Python 3.12, `AUTH_USER_MODEL = "accounts.User"` (AbstractUser)

## Docker

```bash
docker-compose up -d
docker-compose exec nekosvan_backend python manage.py migrate
```

Services: `nekosvan_db` (Postgres), `nekosvan_backend` (Django on `apiserver:8000`, healthcheck on `/health/`), `nekosvan_frontend` (nginx), `nekosvan_onlyoffice` (JWT configurable via env). All on `nekosvan_network` bridge. ONLYOFFICE callback uses internal hostname `http://apiserver:8000/api/v1/documents/callback/`.

ONLYOFFICE JWT: set `ONLYOFFICE_JWT_ENABLED=true` and `ONLYOFFICE_JWT_SECRET=<secret>` in env. Works without JWT when not configured (graceful degradation).
