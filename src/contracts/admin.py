from django.contrib import admin

from .models import Contract, ContractTemplate, Payment


@admin.register(ContractTemplate)
class ContractTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ("deal", "status", "signed_at", "created_at")
    list_filter = ("status",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("deal", "type", "amount", "status", "due_date", "paid_at")
    list_filter = ("type", "status")
