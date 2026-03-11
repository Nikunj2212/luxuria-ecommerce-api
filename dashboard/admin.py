from django.contrib import admin
from .models import Deal

@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "discount_percent",
        "expiry",
        "is_active",
    )

    list_filter = (
        "expiry",
    )

    search_fields = (
        "product__name",
    )

    readonly_fields = (
        "created_at",
    )
