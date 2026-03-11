from django.db import models
from django.utils import timezone
from products.models import Product
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Deal(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="deals"
    )

    # 🔥 CHANGE HERE
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )

    expiry = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_active(self):
        return self.expiry > timezone.now()

    @property
    def discounted_price(self):
        if self.is_active and self.discount_percent:
            discount = (self.product.price * self.discount_percent) / Decimal(100)
            return self.product.price - discount
        return self.product.price

    def __str__(self):
        return f"{self.product.name} Deal"
    
class DashboardAdmin(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username
