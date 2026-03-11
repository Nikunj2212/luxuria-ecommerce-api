from django.contrib import admin
from .models import Product
from .models import ProductReview


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "category",
        "subcategory",
    )

    list_filter = (
        "category",
        "subcategory",
    )

    search_fields = (
        "name",
    )
    
    
@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating',)