from django.contrib import admin

from .models import ClientCompany, Deal, DealActivity


class DealActivityInline(admin.TabularInline):
    model = DealActivity
    extra = 0
    readonly_fields = ("user", "action", "note", "created_at")


@admin.register(ClientCompany)
class ClientCompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_name", "email", "ico", "created_at")
    search_fields = ("name", "ico", "email", "contact_name")


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ("client_company", "phase", "status", "assigned_to", "updated_at")
    list_filter = ("phase", "status", "assigned_to")
    search_fields = ("client_company", "client_contact_name", "client_email")
    readonly_fields = ("portal_token", "created_at", "updated_at", "phase_changed_at")
    inlines = [DealActivityInline]


@admin.register(DealActivity)
class DealActivityAdmin(admin.ModelAdmin):
    list_display = ("deal", "user", "action", "created_at")
    list_filter = ("action",)
    readonly_fields = ("created_at",)
