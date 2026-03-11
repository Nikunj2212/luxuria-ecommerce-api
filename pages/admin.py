from django.contrib import admin
from django.utils.html import format_html
from .models import HomeSlider

@admin.register(HomeSlider)
class HomeSliderAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'preview_image',
        'button_text',
        'redirect_link',
        'is_active',
        'created_at',
    )

    def preview_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:50px;" />',
                obj.image.url
            )
        return "-"

    def redirect_link(self, obj):
        if obj.redirect_url:
            return format_html('<a href="{}" target="_blank">Open</a>', obj.redirect_url)
        return "-"
