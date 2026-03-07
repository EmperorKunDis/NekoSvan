from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Company, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "role", "company", "is_active")
    list_filter = ("role", "company", "is_active")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Profil", {"fields": ("role", "company", "phone")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Profil", {"fields": ("role", "company", "phone")}),
    )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "legal_name", "ico", "email")
