from django.db import models
from django.conf import settings
from products.models import Product


# =========================
# ORDER MODEL
# =========================
class Order(models.Model):
    order_id = models.CharField(max_length=100, unique=True)

    # 🔥 MOST IMPORTANT: order must belong to a user
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()

    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)

    payment_method = models.CharField(
        max_length=20,
        choices=[
            ("ONLINE", "Online"),
            ("COD", "Cash on Delivery")
        ]
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
    max_length=30,
    choices=[
        ('paid', 'Paid'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ],
    default='paid'
)


    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_id} - {self.user.username}"


# =========================
# SHIPPING ADDRESS (ORDER BASED)
# =========================
class ShippingAddress(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="shipping"
    )

    name = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name} - {self.city}"


# =========================
# ORDER ITEMS
# =========================
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

# =========================
# CART MODEL
# =========================
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    
    

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount = models.IntegerField(help_text="Percentage discount")
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

class Wallet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.user.username



