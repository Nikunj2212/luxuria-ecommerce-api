from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='subcategories/', blank=True, null=True)

    def __str__(self):
        return f"{self.category.name} → {self.name}"
    

class Offer(models.Model):
    name = models.CharField(max_length=100)
    discount = models.PositiveIntegerField(help_text="Enter % discount")
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.discount}%)"
    
    
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    category = models.ForeignKey('products.Category', on_delete=models.CASCADE)
    subcategory = models.ForeignKey(
        'products.SubCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    image = models.ImageField(upload_to='products/')
    is_best = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
class ProductReview(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField()
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.rating}⭐"