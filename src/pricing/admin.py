from django.contrib import admin

from .models import Proposal


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ("deal", "version", "total_price", "status", "valid_until", "created_at")
    list_filter = ("status",)
    readonly_fields = ("created_at", "updated_at")
