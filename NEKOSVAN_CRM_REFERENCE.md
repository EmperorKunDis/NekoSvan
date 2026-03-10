# NekoSvan CRM — Kompletní referenční příručka

Kompletní výpis všech funkcí, rolí a prvků systému NekoSvan CRM.

---

## Uživatelské role (5)

| Role | Kdo | Zodpovědnost |
|------|-----|--------------|
| **ADAM** | Adam (ADNP) | Smlouvy, platby, finanční schválení |
| **VADIM** | Vadim | Kvalifikace, prezentace, klientské vztahy |
| **MARTIN** | Martin (Praut) | Cenotvorba, řízení projektů, dohled nad QA |
| **NEKOSVAN** | NekoSvan | Kontrola kvality, QA checklist, review milníků |
| **CLIENT** | Klient | Přístup pouze přes klientský portál |

### User model — pole
- `username`, `email`, `first_name`, `last_name`, `password`
- `role` — výběr z 5 rolí
- `company` — FK na Company (interní firma: ADNP, NekoSvan, Praut), nullable
- `phone`, `bio`, `avatar` (ImageField)
- `is_master` — může vytvářet členy týmu se stejnou rolí
- `created_by` — self-FK (kdo vytvořil)

### Company model (interní firmy)
- `name` — výběr: adnp, nekosvan, praut
- `legal_name`, `ico`, `dic`, `address`, `email`, `phone`
- `created_at`

---

## Pipeline — 8fázový workflow

### Fáze dealu a auto-přiřazení

| # | Fáze | Přiřazeno | Vedlejší efekty |
|---|------|-----------|-----------------|
| 1 | **LEAD** | — | Nové dealy se okamžitě posunou do kvalifikace |
| 2 | **QUALIFICATION** | Vadim (Sales) | Notifikace + N8N webhook |
| 3 | **PRICING** | Martin (PM) | Kalkulace nabídky z dotazníku |
| 4 | **PRESENTATION** | Vadim (Sales) | Klient vidí nabídku na portálu |
| 5 | **CONTRACT** | Adam (Smlouvy) | Generování PDF smlouvy |
| 6 | **PLANNING** | Martin (PM) | **Auto-vytvoření projektu** s milníky |
| 7 | **DEVELOPMENT** | Martin (PM) | Práce na milnících, QA review |
| 8 | **COMPLETED** | NekoSvan (QA) | Finální QA checklist |

### Validátory přechodů

| Cílová fáze | Požadavek |
|-------------|-----------|
| PRICING | Vyplněný dotazník |
| PRESENTATION | Alespoň 1 nabídka |
| CONTRACT | Přijatá nabídka (status=accepted) |
| PLANNING | Podepsaná smlouva (status=signed) |
| COMPLETED | Všechny milníky schváleny |

### Revize
- Pouze z PRESENTATION → PRICING
- Max 3 revize → deal se automaticky archivuje
- `revision_count` na Deal modelu

### Deal model — pole
- **Klientská data (strukturovaná)**: `client` — FK na ClientCompany (preferovaný způsob)
- **Klientská data (plochá, deprecated)**: `client_company`, `client_contact_name`, `client_email`, `client_phone`, `client_ico`
- `description` — popis projektu
- **Pipeline stav**: `phase` (8 fází), `status` (active/archived/on_hold), `assigned_to` (FK na User)
- **Portal**: `portal_token` (UUID), `portal_token_expires_at` (90 dní default), `portal_token_last_accessed_at`
- `revision_count`, `created_by`, `created_at`, `updated_at`, `phase_changed_at`
- **Metody**: `get_client_data()`, `is_portal_token_valid()`, `refresh_portal_token(days=90)`

### ClientCompany model
- `name`, `contact_name`, `email`, `phone`, `ico`, `address`, `notes`
- `created_at`

### DealActivity model (audit log)
- `deal` (FK), `user` (FK, nullable), `action`, `note`, `created_at`
- Zaznamenává: fázové přechody, revize, archivace, portálové přístupy

### LeadDocument model (vytvoření leadu z dokumentu)
- `file` / `raw_text` — vstupní data
- `document_type`: email, brief, rfp, meeting_notes, other
- `status`: pending, processing, processed, failed
- `extracted_data` (JSONField) — data extrahovaná AI
- `deal` (FK, nullable) — výsledný deal
- `uploaded_by`, `created_at`, `processed_at`, `error_message`

---

## Dotazník (84+ polí, 13 sekcí)

### Sekce A — Klient a kontext (10 polí)
| Pole | Typ | Popis |
|------|-----|-------|
| `a_company_name` | CharField | Název firmy |
| `a_ico` | CharField | IČO |
| `a_contact_person` | CharField | Kontaktní osoba |
| `a_email` | EmailField | Email |
| `a_phone` | CharField | Telefon |
| `a_industry` | CharField (choices) | Odvětví: IT, e-shop, výroba, finance, zdravotnictví, vzdělávání, reality, logistika, gastro, služby, neziskovka, vláda, jiné |
| `a_employee_count` | CharField (choices) | Počet zaměstnanců: solo, micro (2-10), small (11-50), medium (51-250), large (250+) |
| `a_annual_revenue` | CharField (choices) | Roční obrat: 5 rozsahů |
| `a_current_it` | JSONField (multi) | Současné IT: website, eshop, crm, erp, accounting, project_mgmt, custom_app, ai_tools, none |
| `a_it_satisfaction` | CharField (choices) | Spokojenost s IT: satisfied, partial, dissatisfied, no_it |

### Sekce B — Typ projektu (4 pole)
| Pole | Typ | Popis |
|------|-----|-------|
| `b_main_categories` | JSONField (multi) | 14 kategorií: custom_dev, website_eshop, ai_automation, enterprise_system, integration, security, data_analytics, support, training, mobile_app, cloud_migration, iot, blockchain, other |
| `b_primary_goal` | CharField (choices) | Hlavní cíl: new_product, digitize, replace, optimize, automate, data, security, other |
| `b_target_users` | JSONField (multi) | Cíloví uživatelé: employees, management, clients, partners, public |
| `b_estimated_users` | CharField (choices) | Odhadovaný počet: 1-5, 6-20, 21-50, 51-200, 201-1000, 1001+, public |

### Sekce C — Custom vývoj (podmíněná, 13 polí)
- `c_platform` — web, mobile_ios, mobile_android, desktop, api_only
- `c_offline_mode` — boolean
- `c_user_roles` — JSONField (admin, manager, editor, viewer, custom)
- `c_auth_methods` — JSONField (email_password, social, sso, 2fa, biometric)
- `c_has_payments` — boolean
- `c_payment_gateway` — stripe, gopay, comgate, paypal, bank_transfer
- `c_multilingual` — boolean
- `c_has_design` — yes_figma, yes_other, no_need, no_dont_need
- `c_key_features` — TextField
- `c_existing_codebase` — boolean
- `c_repo_access` — TextField

### Sekce D — Web & E-shop (podmíněná, 8 polí)
- `d_website_type` — presentation, eshop, catalog, portal, landing, blog
- `d_product_count` — 4 rozsahy
- `d_erp_connection`, `d_has_domain`, `d_has_hosting`
- `d_seo_requirements`, `d_content_management`, `d_preferred_cms`

### Sekce E — AI & automatizace (podmíněná, 6 polí)
- `e_ai_solution_type` — chatbot, data_analysis, document_processing, recommendation, prediction, automation, image_recognition
- `e_data_sources`, `e_data_volume`, `e_gdpr_sensitivity`
- `e_existing_model`, `e_model_accuracy_priority`

### Sekce F — Enterprise systémy (podmíněná, 5 polí)
- `f_system_type` — CRM, ERP, HRM, DMS, project_mgmt, accounting, warehouse
- `f_data_migration` — yes, no, partial
- `f_concurrent_users`, `f_availability_requirements`, `f_legacy_integration`

### Sekce G — Integrace (podmíněná, 3 pole)
- `g_systems_to_connect` — JSONField (multi)
- `g_integration_direction` — one_way, two_way, both
- `g_sync_frequency` — realtime, hourly, daily, weekly, manual

### Sekce H — Bezpečnost (podmíněná, 3 pole)
- `h_security_service_type` — audit, pentest, monitoring, incident_response, compliance, training
- `h_had_incident` — boolean
- `h_regulatory_requirements` — JSONField (multi)

### Sekce I — Data & analytika (podmíněná, 4 pole)
- `i_data_needs` — dashboards, reports, ETL, data_warehouse, visualization
- `i_data_sources`, `i_existing_bi_tool`, `i_report_users`

### Sekce J — Podpora & školení (podmíněná, 6 polí)
- `j_support_type` — helpdesk, monitoring, maintenance, on_call, consulting
- `j_required_sla` — CharField (choices)
- `j_training_type` — online, onsite, video, documentation
- `j_training_count` — PositiveInteger
- `j_training_format` — group, individual, both

### Sekce K — Budget a timeline (vždy viditelná, 8 polí)
| Pole | Možnosti |
|------|----------|
| `k_budget_range` | under_50k, 50k_150k, 150k_500k, 500k_1m, 1m_3m, over_3m, not_specified |
| `k_pricing_model` | fixed, time_material, retainer, milestone, no_preference |
| `k_launch_deadline` | asap, 1month, 3months, 6months, year, flexible |
| `k_specific_deadline` | DateField |
| `k_prefers_mvp` | yes, no, unknown |
| `k_priority` | speed, quality, price, innovation |
| `k_decision_maker` | contact, board, team |
| `k_decision_horizon` | immediately, weeks, months, exploring |

### Sekce L — Technické preference (podmíněná: budget >= 500k, 6 polí)
- `l_has_it_team` — boolean
- `l_preferred_stack` — python, javascript, typescript, java, dotnet, php, go, rust
- `l_hosting_preference` — cloud_cz, cloud_eu, cloud_global, on_premise, no_preference
- `l_database_preference` — postgresql, mysql, mssql, mongodb, no_preference
- `l_cicd_devops` — boolean
- `l_code_ownership` — boolean

### Sekce M — Závěr hovoru (5 polí)
- `m_lead_source` — referral, google, social, event, cold, returning, other
- `m_next_step` — proposal, meeting, demo, waiting, declined
- `m_next_contact_date` — DateField
- `m_sales_notes` — TextField
- `m_lead_rating` — hot, warm, cool, cold

### AI pole
- `ai_raw_text` — TextField (vložený text pro AI extrakci)
- `ai_raw_file` — FileField (soubor pro AI extrakci)

---

## Cenotvorba (Pricing)

### PricingMatrix model
| Pole | Popis |
|------|-------|
| `category` | Unikátní klíč kategorie (custom_dev, website_eshop, ...) |
| `base_hours` | Základní hodinová dotace (80–200h) |
| `hourly_rate` | Hodinová sazba (výchozí 1500 Kč) |
| `is_active` | Aktivní/neaktivní |

**Fallback hodnoty** (pokud DB prázdná):
| Kategorie | Hodiny |
|-----------|--------|
| custom_dev | 160h |
| website_eshop | 80h |
| ai_automation | 120h |
| enterprise_system | 200h |
| integration | 60h |
| security | 40h |
| data_analytics | 80h |
| support | 20h |
| training | 16h |
| mobile_app | 160h |
| cloud_migration | 80h |
| iot | 120h |
| blockchain | 160h |
| other | 80h |

### PricingModifier model
| Pole | Popis |
|------|-------|
| `modifier_type` | user_count, complexity, design, platform |
| `key` | Klíč hodnoty (např. "1_5", "6_20") |
| `multiplier` | Násobitel (výchozí 1.0) |
| `extra_hours` | Extra hodiny k přičtení |

### Kalkulace nabídky — logika `calculate_proposal()`
1. Součet základních hodin z vybraných `b_main_categories` (PricingMatrix)
2. Aplikace multiplikátoru podle `b_estimated_users` (1.0x–2.0x)
3. Extra hodiny za platformy (pokud více platforem)
4. Hodiny za design (pokud `c_has_design` != "no_dont_need")
5. Integrace: 16h × počet systémů v `g_systems_to_connect`
6. Bezpečnost: 12h × počet služeb v `h_security_service_type`
7. Migrace dat: 24h (yes) nebo 12h (partial) podle `f_data_migration`
8. Školení: 8h × počet typů v `j_training_type`
9. Podpora: 8h × počet typů v `j_support_type`
10. **Záloha = 30 % z celkové ceny**

### Proposal model (nabídka)
| Pole | Popis |
|------|-------|
| `deal` | FK na Deal |
| `version` | Číslo verze (inkrementální) |
| `status` | draft, sent, accepted, rejected, expired |
| `items` | JSONField: `[{"name": "...", "hours": 10, "rate": 1500, "total": 15000}]` |
| `base_price` | Základní cena |
| `total_price` | Celková cena |
| `deposit_amount` | Záloha |
| `valid_until` | Platnost do |
| `demo_url`, `demo_description` | Demo odkaz |
| `client_feedback` | Zpětná vazba klienta |
| `created_by`, `created_at`, `updated_at` | Metadata |

---

## Smlouvy a platby

### ContractTemplate model
- `name` — název šablony
- `body_template` — tělo s placeholdery: `{{client_name}}`, `{{total_price}}`, `{{deposit_amount}}`, atd.
- `is_active`

### Contract model
| Pole | Popis |
|------|-------|
| `deal` | OneToOne FK na Deal |
| `template_used` | FK na ContractTemplate |
| `generated_pdf` | FileField (WeasyPrint výstup) |
| `status` | draft, sent, signed, cancelled |
| `signed_at` | Datum podpisu |
| `signed_by_client` | Boolean |

### Payment model
| Pole | Popis |
|------|-------|
| `deal` | FK na Deal |
| `type` | deposit, milestone, final |
| `status` | pending, paid, overdue |
| `amount` | DecimalField |
| `due_date` | DateField |
| `paid_at` | DateTimeField |
| `invoice_number` | CharField |

### Auto-vytvoření plateb (při podpisu smlouvy)
1. **Záloha**: `amount = proposal.deposit_amount`, splatnost +14 dní
2. **Závěrečná platba**: `amount = total - deposit`, splatnost +90 dní
3. Po zaplacení zálohy → deal se automaticky posune CONTRACT → PLANNING

---

## Projekty a milníky

### MilestoneTemplate model
- `name`, `category` (klíč typu projektu), `is_default`, `is_active`

### MilestoneTemplateItem model
- `template` (FK), `title`, `description`, `rich_description`
- `deliverables`, `acceptance_criteria` (řádkově oddělený text)
- `order`, `estimated_hours`

### Project model
| Pole | Popis |
|------|-------|
| `deal` | OneToOne FK na Deal |
| `status` | planning, in_progress, review, completed, support |
| `implementation_plan` | TextField |
| `start_date`, `estimated_end_date`, `actual_end_date` | Datumy |
| `progress_percent` | Computed property (% schválených milníků) |

**Auto-vytvoření** (při přechodu do PLANNING):
- Vytvoří Project
- Vytvoří milníky z MilestoneTemplate (podle kategorie) nebo fallback:
  1. Analýza a plánování
  2. Implementace
  3. Testování a QA
  4. Deploy a předání

### Milestone model — QA & klientský review workflow
| Pole | Popis |
|------|-------|
| `project` | FK na Project |
| `title`, `description` | Popis milníku |
| `order` | Pořadí |
| `due_date` | Termín |
| `status` | pending, in_progress, qa_review, client_review, approved, rejected |
| `dev_completed_at` | Kdy Martin dokončil vývoj |
| `qa_approved_at` | Kdy NekoSvan schválil QA |
| `client_approved_at` | Kdy klient schválil |
| `client_feedback` | Zpětná vazba |
| `demo_url` | URL demo |

**Workflow milníku:**
```
PENDING → IN_PROGRESS → QA_REVIEW → CLIENT_REVIEW → APPROVED
                ↑           ↓              ↓
                ← (QA reject) ←    (Client reject → REJECTED)
```
1. Martin označí `dev_complete` → **QA_REVIEW** (notifikace NekoSvan)
2. NekoSvan schválí → **CLIENT_REVIEW** (notifikace Vadim) NEBO zamítne → zpět **IN_PROGRESS**
3. Klient (přes portál) schválí → **APPROVED** NEBO zamítne → **REJECTED**

### QAChecklist model (finální kontrola projektu)
10 boolean položek:
| Položka | Popis |
|---------|-------|
| `performance_ok` | Výkon v pořádku |
| `security_ok` | Bezpečnost ověřena |
| `responsive_ok` | Responsivní design |
| `cross_browser_ok` | Funkční ve všech prohlížečích |
| `seo_ok` | SEO optimalizace |
| `accessibility_ok` | Přístupnost |
| `backup_ok` | Zálohy nastaveny |
| `monitoring_ok` | Monitoring nastaven |
| `documentation_ok` | Dokumentace kompletní |
| `client_training_ok` | Klient proškolen |

- `is_complete` — property: všech 10 checked
- `completion_percent` — property: % dokončení
- `checked_by`, `completed_at`

### ProjectComment model
- `project` (FK), `milestone` (FK, nullable), `user` (FK)
- `text`, `created_at`

### TemplateComment model
- `template` (FK), `template_item` (FK, nullable), `user` (FK)
- `text`, `is_resolved`, `resolved_by`, `resolved_at`

---

## Dokumenty (ONLYOFFICE integrace)

### Document model
| Pole | Popis |
|------|-------|
| `id` | UUIDField (primární klíč) |
| `title` | Název dokumentu |
| `document_type` | contract, proposal, brief, meeting_notes, other |
| `file` | FileField |
| `file_type` | docx, xlsx, pptx, pdf, doc, odt, rtf, txt, xls, ods, csv, ppt, odp |
| `deal` | FK (nullable) |
| `project` | FK (nullable) |
| `created_by`, `last_modified_by` | FK na User |
| `key` | UUID klíč pro ONLYOFFICE verzování |
| `created_at`, `updated_at` | Timestampy |

### DocumentVersion model
- `document` (FK), `version` (int), `file`, `created_by`, `created_at`, `changes_description`

### ONLYOFFICE JWT
- `generate_onlyoffice_token(payload)` — HS256, vrací "" pokud secret nenastavený
- `verify_onlyoffice_token(token)` — vrací None při invalidním, {} pokud secret nenastavený
- `ONLYOFFICE_JWT_SECRET` — env var (volitelný)

---

## Notifikace (duální kanál + SSE)

### Notification model
| Pole | Popis |
|------|-------|
| `user` | FK na User |
| `deal` | FK na Deal (nullable) |
| `title`, `message`, `link` | Obsah notifikace |
| `notification_type` | in_app, email, webhook |
| `delivery_status` | pending, delivered, failed |
| `read` | Boolean |
| `created_at` | Timestamp |

### Webhookové události (N8N)
| Událost | Kdy nastane |
|---------|-------------|
| `deal.created` | Nový lead vytvořen |
| `deal.phase_changed` | Deal postoupil do další fáze |
| `deal.inactive_48h` | Deal neaktivní 48+ hodin (Celery periodic) |
| `deal.archived` | Deal archivován (max revizí) |
| `questionnaire.completed` | Dotazník vyplněn |
| `proposal.accepted` | Klient přijal nabídku |
| `proposal.rejected` | Klient odmítl nabídku |
| `contract.signed` | Smlouva podepsána |
| `payment.received` | Platba přijata |
| `payment.overdue` | Platba po splatnosti (Celery periodic) |
| `milestone.ready_for_review` | Milník připraven na QA review |
| `milestone.approved` | Klient schválil milník |
| `qa.issue_found` | QA zamítl milník |

### Circuit breaker (N8N)
- 5 selhání → otevřený na 5 minut
- Stav uložen v Redis cache
- Exponenciální backoff: 30s → max 300s
- Max 5 retries

### SSE endpoint
- `GET /api/v1/notifications/stream/` — StreamingHttpResponse
- Poll DB co 5s + heartbeat
- Frontend: EventSource s auto-reconnect (fallback 30s)

---

## Klientský portál (bez autentizace)

### Přístup
- UUID token v URL: `/portal/{token}/`
- Žádný login — `AllowAny` permission
- Token expiruje po 90 dnech (konfigurovatelné)
- Rate limiting: čtení 30/min, zápis 10/min
- Každý přístup logován (IP + user-agent → DealActivity)

### Endpointy portálu
| URL | Metoda | Akce |
|-----|--------|------|
| `/{token}/` | GET | Dashboard — deal, nabídka, smlouva, platby, projekt |
| `/{token}/proposal/accept/` | POST | Přijetí nabídky → deal do CONTRACT |
| `/{token}/proposal/reject/` | POST | Odmítnutí nabídky + feedback → revision |
| `/{token}/milestone/{id}/approve/` | POST | Schválení milníku |
| `/{token}/milestone/{id}/reject/` | POST | Zamítnutí milníku + feedback |
| `/{token}/contract/download/` | GET | Stažení PDF smlouvy |

---

## Celery úlohy

### Periodické (každou hodinu)
| Úloha | Popis |
|-------|-------|
| `check_inactive_deals` | Najde dealy neaktivní 48+ hodin, pošle upomínku |
| `check_overdue_payments` | Označí platby po splatnosti, triggeruje N8N |

### On-demand
| Úloha | Popis |
|-------|-------|
| `generate_contract_pdf_task(deal_id)` | Async generování PDF přes WeasyPrint |
| `send_n8n_webhook(event, payload)` | Async N8N webhook s circuit breakerem |

### Hardening (všechny úlohy)
- `autoretry_for=(Exception,)`, exponenciální backoff 60s → max 600s
- `max_retries=3`, `soft_time_limit=120s`, `time_limit=180s`, `acks_late=True`

---

## Django signály

| Signál | Kdy emitován | Parametry |
|--------|--------------|-----------|
| `deal_phase_changed` | `advance_phase()` | deal, old_phase, new_phase, user, note |
| `deal_revision_requested` | `request_revision()` | deal, user, feedback |
| `deal_archived` | `request_revision()` při max revizích | deal, reason |

### Receivery
- `projects.receivers.auto_create_project` — reaguje na PLANNING fázi → vytvoří projekt
- `notifications.receivers.notify_on_phase_change` — notifikace při změně fáze

---

## Permission classes

### Sémantické (nové, preferované)
| Třída | Povolené role |
|-------|---------------|
| `IsContractManager` | ADAM |
| `IsSalesLead` | VADIM |
| `IsProjectManager` | MARTIN |
| `IsQAReviewer` | MARTIN, NEKOSVAN |

### Deprecated (funkční, ale s varováním)
| Třída | Nahrazena |
|-------|-----------|
| `IsAdam` | IsContractManager |
| `IsVadim` | IsSalesLead |
| `IsMartin` | IsProjectManager |
| `IsNekoSvan` | IsQAReviewer |

### Generické
| Třída | Popis |
|-------|-------|
| `IsInternalUser` | Jakýkoliv role kromě CLIENT |
| `DealPhasePermission` | Interní uživatel, object-level |
| `ProposalPermission` | Interní uživatel |
| `ContractPermission` | Interní uživatel |
| `PaymentPermission` | Interní uživatel |
| `MilestoneActionPermission` | Interní uživatel |
| `IsMartinRole` | Martin může zapisovat, ostatní jen číst |
| `IsQARole` | Martin nebo NekoSvan |

---

## API endpointy — kompletní seznam

### Pipeline `/api/v1/pipeline/`
| Metoda | URL | Popis |
|--------|-----|-------|
| GET | `/deals/` | Seznam dealů (filtr: phase, status, assigned_to) |
| POST | `/deals/` | Vytvoření dealu (auto-advance lead→qualification) |
| GET | `/deals/{id}/` | Detail dealu |
| PATCH | `/deals/{id}/` | Úprava dealu |
| POST | `/deals/{id}/advance/` | Posun do další fáze |
| POST | `/deals/{id}/revision/` | Žádost o revizi (PRESENTATION→PRICING) |
| GET | `/deals/{id}/timeline/` | Historie aktivit dealu |
| POST | `/deals/{id}/refresh-portal-token/` | Nový portálový token |
| DELETE | `/deals/{id}/` | Soft delete (archivace) |
| DELETE | `/deals/{id}/hard-delete/` | Permanentní smazání |
| GET | `/deal-activities/` | Všechny aktivity |
| POST | `/lead-from-document/` | Vytvoření leadu z dokumentu/textu (AI extrakce) |
| GET | `/dashboard/` | Dashboard: dealy podle fází, přiřazení, aktivita |

### Dotazník `/api/v1/questionnaire/`
| Metoda | URL | Popis |
|--------|-----|-------|
| GET | `/questionnaires/` | Seznam (filtr: deal) |
| POST | `/questionnaires/` | Vytvoření (auto-advance qualification→pricing) |
| PATCH | `/questionnaires/{id}/` | Úprava |
| POST | `/questionnaires/ai-extract/` | AI extrakce z textu/souboru (Ollama) |

### Cenotvorba `/api/v1/pricing/`
| Metoda | URL | Popis |
|--------|-----|-------|
| GET | `/pricing-matrix/` | Seznam pricing matice |
| POST | `/pricing-matrix/` | Vytvoření (jen Martin) |
| PATCH | `/pricing-matrix/{id}/` | Úprava (jen Martin) |
| GET | `/pricing-modifiers/` | Seznam modifikátorů |
| POST | `/pricing-modifiers/` | Vytvoření (jen Martin) |
| PATCH | `/pricing-modifiers/{id}/` | Úprava (jen Martin) |
| GET | `/proposals/` | Seznam nabídek (filtr: deal, status) |
| POST | `/proposals/` | Vytvoření nabídky |
| PATCH | `/proposals/{id}/` | Úprava |
| GET | `/proposals/auto-calculate/{deal_id}/` | Auto-kalkulace z dotazníku |
| POST | `/proposals/{id}/send/` | Odeslání klientovi |

### Smlouvy `/api/v1/contracts/`
| Metoda | URL | Popis |
|--------|-----|-------|
| GET | `/contract-templates/` | Seznam šablon |
| POST | `/contract-templates/` | Vytvoření šablony |
| PATCH | `/contract-templates/{id}/` | Úprava |
| GET | `/contracts/` | Seznam smluv (filtr: deal, status) |
| POST | `/contracts/generate/{deal_id}/` | Generování PDF (async) |
| POST | `/contracts/{id}/send-to-client/` | Odeslání klientovi |
| POST | `/contracts/{id}/mark-signed/` | Označení jako podepsaná (auto-create platby) |
| GET | `/payments/` | Seznam plateb (filtr: deal, type, status) |
| POST | `/payments/` | Vytvoření platby |
| POST | `/payments/{id}/mark-paid/` | Označení jako zaplacená |

### Projekty `/api/v1/projects/`
| Metoda | URL | Popis |
|--------|-----|-------|
| GET | `/projects/` | Seznam projektů (filtr: deal, status) |
| POST | `/projects/create-from-deal/{deal_id}/` | Ruční vytvoření projektu |
| GET | `/milestones/` | Seznam milníků (filtr: project, status) |
| POST | `/milestones/{id}/dev-complete/` | Martin: dev hotov |
| POST | `/milestones/{id}/qa-approve/` | NekoSvan: QA schválení |
| POST | `/milestones/{id}/qa-reject/` | NekoSvan: QA zamítnutí |
| POST | `/milestones/{id}/client-approve/` | Klient: schválení |
| POST | `/milestones/{id}/client-reject/` | Klient: zamítnutí |
| GET | `/milestone-templates/` | Seznam šablon milníků |
| POST | `/milestone-templates/` | Vytvoření šablony (jen Martin) |
| PATCH | `/milestone-templates/{id}/` | Úprava |
| POST | `/milestone-templates/{id}/add-item/` | Přidání položky |
| GET | `/milestone-templates/{id}/comments/` | Komentáře šablony |
| POST | `/milestone-templates/{id}/comments/` | Přidání komentáře |
| GET | `/qa-checklists/` | Seznam QA checklistů |
| POST | `/qa-checklists/` | Vytvoření |
| PATCH | `/qa-checklists/{id}/` | Úprava |
| POST | `/qa-checklists/{id}/complete/` | Dokončení (vše musí být checked) |
| GET | `/project-comments/` | Seznam komentářů |
| POST | `/project-comments/` | Přidání komentáře |
| GET | `/template-comments/` | Seznam komentářů šablon |
| POST | `/template-comments/` | Přidání |
| POST | `/template-comments/{id}/resolve/` | Označení jako vyřešený |
| POST | `/template-comments/{id}/unresolve/` | Zrušení vyřešení |

### Notifikace `/api/v1/notifications/`
| Metoda | URL | Popis |
|--------|-----|-------|
| GET | `/notifications/` | Seznam notifikací (filtr: read, deal) |
| POST | `/notifications/{id}/mark-read/` | Označení jako přečtená |
| POST | `/notifications/mark-all-read/` | Označit vše jako přečtené |
| GET | `/notifications/unread-count/` | Počet nepřečtených |
| GET | `/stream/` | SSE real-time notifikace |

### Dokumenty `/api/v1/documents/`
| Metoda | URL | Popis |
|--------|-----|-------|
| GET | `/documents/` | Seznam (filtr: type, deal, project) |
| POST | `/documents/` | Upload dokumentu |
| PATCH | `/documents/{id}/` | Úprava |
| DELETE | `/documents/{id}/` | Smazání |
| GET | `/documents/{id}/onlyoffice-config/` | ONLYOFFICE konfigurace + JWT |
| GET | `/documents/{id}/versions/` | Historie verzí |
| POST | `/documents/{id}/regenerate-key/` | Nový klíč (force reload) |
| POST | `/callback/` | ONLYOFFICE callback (bez auth) |

### Účty `/api/v1/accounts/`
| Metoda | URL | Popis |
|--------|-----|-------|
| POST | `/login/` | Přihlášení (session) |
| POST | `/logout/` | Odhlášení |
| GET | `/csrf-token/` | CSRF token |
| GET | `/users/` | Seznam uživatelů |
| POST | `/users/` | Vytvoření uživatele |
| GET | `/users/me/` | Aktuální uživatel |
| PATCH | `/users/{id}/` | Úprava |
| GET | `/companies/` | Seznam firem |
| POST | `/companies/` | Vytvoření |
| PATCH | `/companies/{id}/` | Úprava |
| GET | `/profile/` | Vlastní profil |
| PATCH | `/profile/` | Úprava profilu |
| POST | `/change-password/` | Změna hesla |
| GET | `/team/` | Tým (jen master users) |
| POST | `/team/` | Vytvoření člena týmu |
| PATCH | `/team/{id}/` | Úprava člena |
| DELETE | `/team/{id}/` | Deaktivace člena |

### Ostatní
| Metoda | URL | Popis |
|--------|-----|-------|
| GET | `/health/` | Health check (DB, Redis, Celery, Ollama, ONLYOFFICE) |
| GET | `/api/docs/` | Swagger UI |
| GET | `/admin/` | Django admin |

---

## Frontend routy (Angular)

| Route | Komponenta | Auth | Účel |
|-------|------------|------|------|
| `/login` | LoginComponent | Ne | Přihlášení |
| `/dashboard` | DashboardComponent | Ano | Hlavní přehled |
| `/deals` | DealListComponent | Ano | Seznam dealů |
| `/deals/new` | DealCreateComponent | Ano | Nový deal |
| `/deals/from-document` | DealFromDocumentComponent | Ano | Deal z dokumentu |
| `/deals/:id` | DealDetailComponent | Ano | Detail dealu |
| `/deals/:id/questionnaire` | QuestionnaireFormComponent | Ano | Formulář dotazníku |
| `/deals/:id/pricing` | PricingComponent | Ano | Cenotvorba/nabídky |
| `/deals/:id/contract` | ContractComponent | Ano | Správa smlouvy |
| `/deals/:id/project` | ProjectDetailComponent | Ano | Detail projektu |
| `/projects` | ProjectListComponent | Ano | Seznam projektů |
| `/qa-queue` | QAQueueComponent | Ano | QA fronta milníků |
| `/payments` | PaymentListComponent | Ano | Seznam plateb |
| `/documents` | DocumentListComponent | Ano | Seznam dokumentů |
| `/documents/:id` | DocumentDetailComponent | Ano | ONLYOFFICE editor |
| `/templates` | TemplateListComponent | Ano | Šablony smluv |
| `/milestone-templates` | MilestoneTemplatesComponent | Ano | Šablony milníků |
| `/pricing-matrix` | PricingMatrixComponent | Ano | Konfigurace pricing matice |
| `/notifications` | NotificationListComponent | Ano | Notifikace |
| `/profile` | ProfileComponent | Ano | Profil uživatele |
| `/team` | TeamComponent | Ano | Správa týmu (master) |
| `/portal/:token` | PortalComponent | Ne | Klientský portál |

---

## Přehled modelů (29 celkem)

| App | Modely |
|-----|--------|
| **accounts** | User, Company |
| **pipeline** | Deal, DealActivity, ClientCompany, LeadDocument |
| **questionnaire** | QuestionnaireResponse |
| **pricing** | PricingMatrix, PricingModifier, Proposal |
| **contracts** | ContractTemplate, Contract, Payment |
| **projects** | MilestoneTemplate, MilestoneTemplateItem, TemplateComment, Project, Milestone, QAChecklist, ProjectComment |
| **notifications** | Notification |
| **documents** | Document, DocumentVersion |

---

## Klíčové systémové toky

### 1. Nový deal
```
POST /deals/ → Deal(LEAD) → auto-advance → Deal(QUALIFICATION, assigned=Vadim)
  → N8N: deal.created → Notification pro Vadima
```

### 2. Vyplnění dotazníku
```
POST /questionnaires/ → QuestionnaireResponse vytvořen
  → auto-advance → Deal(PRICING, assigned=Martin)
  → N8N: questionnaire.completed
```

### 3. Nabídka → prezentace
```
POST /proposals/{id}/send/ → Proposal(sent)
  → auto-advance → Deal(PRESENTATION, assigned=Vadim)
  → Klient dostane portal link
```

### 4. Rozhodnutí klienta na portálu
```
Klient přijme: Proposal(accepted) → Deal(CONTRACT, assigned=Adam)
Klient odmítne: Proposal(rejected) → revision → Deal(PRICING, assigned=Martin)
3× odmítnutí → Deal(ARCHIVED)
```

### 5. Smlouva → projekt
```
Contract(signed) → auto-create Payment(deposit, 14d) + Payment(final, 90d)
Payment(deposit, paid) → Deal(PLANNING, assigned=Martin)
  → auto-create Project + Milestones
```

### 6. Milník review workflow
```
Martin: dev_complete → Milestone(QA_REVIEW) → NekoSvan notifikován
NekoSvan: qa_approve → Milestone(CLIENT_REVIEW) → Vadim notifikován
  NEBO: qa_reject → Milestone(IN_PROGRESS) → Martin notifikován
Klient (portál): approve → Milestone(APPROVED)
  NEBO: reject → Milestone(REJECTED)
```

### 7. Finální QA
```
NekoSvan: vyplní 10-položkový QA checklist
Vše OK → Deal(COMPLETED)
```
