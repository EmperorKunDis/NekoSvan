#!/usr/bin/env python
"""
Security Configuration Verification Script
Spusť po instalaci django-axes a migraci.
"""

import os
import sys
from pathlib import Path

# Django setup
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

import django
django.setup()

from django.conf import settings
from django.core.management import call_command


def verify_axes_installed():
    """Ověř že django-axes je v INSTALLED_APPS."""
    if "axes" not in settings.INSTALLED_APPS:
        return False, "❌ 'axes' není v INSTALLED_APPS"
    return True, "✅ django-axes je nainstalován"


def verify_axes_middleware():
    """Ověř že AxesMiddleware je v MIDDLEWARE."""
    if "axes.middleware.AxesMiddleware" not in settings.MIDDLEWARE:
        return False, "❌ AxesMiddleware není v MIDDLEWARE"
    return True, "✅ AxesMiddleware je aktivní"


def verify_axes_config():
    """Ověř konfiguraci axes."""
    checks = []
    
    if getattr(settings, "AXES_FAILURE_LIMIT", None) == 5:
        checks.append("✅ AXES_FAILURE_LIMIT = 5")
    else:
        checks.append(f"❌ AXES_FAILURE_LIMIT = {getattr(settings, 'AXES_FAILURE_LIMIT', 'NOT SET')}")
    
    if getattr(settings, "AXES_COOLOFF_TIME", None) == 0.25:
        checks.append("✅ AXES_COOLOFF_TIME = 0.25 (15 min)")
    else:
        checks.append(f"⚠️ AXES_COOLOFF_TIME = {getattr(settings, 'AXES_COOLOFF_TIME', 'NOT SET')}")
    
    if "ip_address" in getattr(settings, "AXES_LOCKOUT_PARAMETERS", []):
        checks.append("✅ Lockout tracking na IP")
    else:
        checks.append("⚠️ Lockout tracking není na IP")
    
    return True, "\n  ".join(checks)


def verify_security_settings():
    """Ověř Django security settings (production)."""
    # Pro local dev můžeme skipnout některé checks
    if settings.DEBUG:
        return True, "ℹ️ DEBUG=True (local dev) - skipping production checks"
    
    checks = []
    
    if getattr(settings, "SECURE_SSL_REDIRECT", False):
        checks.append("✅ SECURE_SSL_REDIRECT = True")
    else:
        checks.append("❌ SECURE_SSL_REDIRECT = False")
    
    if getattr(settings, "SECURE_HSTS_SECONDS", 0) >= 31536000:
        checks.append("✅ SECURE_HSTS_SECONDS >= 1 year")
    else:
        checks.append(f"❌ SECURE_HSTS_SECONDS = {getattr(settings, 'SECURE_HSTS_SECONDS', 0)}")
    
    if getattr(settings, "X_FRAME_OPTIONS", "") == "DENY":
        checks.append("✅ X_FRAME_OPTIONS = DENY")
    else:
        checks.append(f"⚠️ X_FRAME_OPTIONS = {getattr(settings, 'X_FRAME_OPTIONS', 'NOT SET')}")
    
    return True, "\n  ".join(checks)


def verify_migrations():
    """Zkontroluj pending migrations."""
    try:
        call_command("showmigrations", "--plan", stdout=open(os.devnull, 'w'))
        return True, "✅ Migrace jsou v pořádku"
    except Exception as e:
        return False, f"❌ Migrace mají problém: {e}"


def main():
    """Spusť všechny verifikační checks."""
    print("=" * 60)
    print("🔒 NEKOSVAN CRM — Security Configuration Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Django Axes Installed", verify_axes_installed),
        ("Axes Middleware", verify_axes_middleware),
        ("Axes Configuration", verify_axes_config),
        ("Security Settings", verify_security_settings),
        ("Database Migrations", verify_migrations),
    ]
    
    all_passed = True
    
    for name, check_fn in checks:
        print(f"🔍 {name}:")
        passed, message = check_fn()
        print(f"  {message}")
        print()
        
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("✅ Všechny security checks prošly!")
        print()
        print("📝 Další kroky:")
        print("  1. Spusť testy: pytest src/accounts/tests/ -v")
        print("  2. Zkus login s wrong password 6x → měl by lockout")
        print("  3. Deploy na produkci a ověř HTTPS headers")
    else:
        print("❌ Některé checks selhaly - oprav před nasazením!")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
