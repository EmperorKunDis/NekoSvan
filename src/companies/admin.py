from django.contrib import admin

from .models import Communication, Company, CompanyContact, CompanyDocument


class CompanyContactInline(admin.TabularInline):
    model = CompanyContact
    extra = 1
    fields = ("name", "position", "email", "phone", "is_primary")


class CommunicationInline(admin.TabularInline):
    model = Communication
    extra = 0
    readonly_fields = ("created_by", "created_at")
    fields = ("type", "subject", "date", "contact", "created_by", "created_at")


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "ico", "city", "status", "sector", "updated_at")
    list_filter = ("status", "sector", "country")
    search_fields = ("name", "ico", "dic", "email", "city")
    readonly_fields = ("created_at", "updated_at")
    inlines = [CompanyContactInline, CommunicationInline]

    fieldsets = (
        (
            "Základní údaje",
            {
                "fields": ("name", "ico", "dic", "status", "sector", "tags"),
            },
        ),
        (
            "Adresa",
            {
                "fields": ("address", "city", "postal_code", "country"),
            },
        ),
        (
            "Kontaktní údaje",
            {
                "fields": ("email", "phone", "website"),
            },
        ),
        (
            "Poznámky",
            {
                "fields": ("notes",),
            },
        ),
        (
            "Časové údaje",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )


@admin.register(CompanyContact)
class CompanyContactAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "position", "email", "is_primary", "created_at")
    list_filter = ("is_primary", "company")
    search_fields = ("name", "email", "company__name")
    readonly_fields = ("created_at",)


@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ("company", "type", "subject", "date", "created_by", "created_at")
    list_filter = ("type", "company")
    search_fields = ("subject", "content", "company__name")
    readonly_fields = ("created_by", "created_at")


@admin.register(CompanyDocument)
class CompanyDocumentAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "document_type", "uploaded_by", "created_at")
    list_filter = ("document_type", "company")
    search_fields = ("name", "company__name")
    readonly_fields = ("uploaded_by", "created_at")
