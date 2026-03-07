# NekoSvan CRM

Workflow Management System pro Praut s.r.o.

## 🚀 Quick Deploy

### Na server (doporučeno)

```bash
./deploy.sh 72.62.92.89 root
```

### Lokálně (development)

```bash
# Backend
cd /path/to/NekoSvan
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 13666

# Frontend (nový terminál)
cd frontend
npm install
ng serve --port 12666 --proxy-config proxy.conf.json
```

## 🐳 Docker Deploy

```bash
# Zkopírovat a upravit env
cp .env.example .env
nano .env

# Spustit
docker-compose up -d

# Migrace
docker-compose exec backend python manage.py migrate
```

## 📁 Struktura

```
NekoSvan/
├── config/              # Django settings
├── src/                 # Django apps
│   ├── accounts/        # Uživatelé, role, týmy
│   ├── pipeline/        # Dealy, fáze, workflow
│   ├── questionnaire/   # Dotazníky
│   ├── pricing/         # Cenotvorba, matice
│   ├── contracts/       # Smlouvy
│   ├── projects/        # Projekty, milníky
│   ├── documents/       # ONLYOFFICE dokumenty
│   ├── notifications/   # Notifikace
│   └── client_portal/   # Klientský portál
├── frontend/            # Angular 19
├── nginx/               # Nginx config
├── docker-compose.yml   # Docker stack
├── deploy.sh           # Deploy script
└── start.sh            # Local dev start
```

## 👥 Role

| Role | Popis | Hlavní fáze |
|------|-------|-------------|
| **Adam (ADNP)** | Obchod, smlouvy | Lead, Contract, Completed |
| **Vadim** | Freelancer, komunikace | Qualification, Presentation |
| **Martin (Praut)** | Vývoj, cenotvorba | Pricing, Planning, Development |
| **NekoSvan** | QA | Všechny fáze |

## 🔗 URLs

| Prostředí | Frontend | Backend | ONLYOFFICE |
|-----------|----------|---------|------------|
| Local | :12666 | :13666 | :9980 |
| Production | praut.cz/app | praut.cz/app/api | praut.cz/app/onlyoffice |

## 🔐 Testovací účty

| Username | Password | Role |
|----------|----------|------|
| adam | changeme123 | Adam (ADNP) - Master |
| vadim | changeme123 | Vadim - Master |
| martin | changeme123 | Martin (Praut) - Master |
| admin | admin123 | Admin (production) |

## 📝 Features

- ✅ 8-fázový deal workflow
- ✅ Role-based dashboards
- ✅ Dotazníky s AI importem
- ✅ Cenotvorba s maticí a modifikátory
- ✅ Generování smluv
- ✅ Projektový management s milníky
- ✅ QA workflow
- ✅ Klientský portál
- ✅ ONLYOFFICE document editor
- ✅ Notifikace
- ✅ Team management (master role)

## 🎨 Branding

Barvy Praut:
- Primary: `#7c3aed` (Purple)
- Secondary: `#06b6d4` (Cyan)
- Background: `#faf5ff`

---

© 2026 Praut s.r.o.
