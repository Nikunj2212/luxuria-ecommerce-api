from rest_framework import serializers
from products.models import Product
from carts.models import Cart
from carts.models import Order
from carts.models import OrderItem
from products.models import Category
from products.models import SubCategory
from products.models import ProductReview
from django.db.models import Avg
from wishlist.models import Wishlist
from dashboard.models import Deal
from contact.models import ContactThread




class ProductSerializer(serializers.ModelSerializer):

    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"

    def get_average_rating(self, obj):
        avg = ProductReview.objects.filter(product=obj).aggregate(Avg('rating'))
        return avg['rating__avg']

    def get_total_reviews(self, obj):
        return ProductReview.objects.filter(product=obj).count()
        
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"
        
class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)
    
class CreateOrderSerializer(serializers.Serializer):

    customer_name = serializers.CharField()
    customer_email = serializers.EmailField()
    phone = serializers.CharField()
    address = serializers.CharField()
    city = serializers.CharField()
    pincode = serializers.CharField()
    payment_method = serializers.CharField()
    
class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = "__all__"
        
class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = "__all__"
        
class OrderDetailSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"
        
class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"
        
class SubCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = SubCategory
        fields = "__all__"
        
class ProductReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductReview
        fields = "__all__"
        read_only_fields = ["user"]
        

class WishlistSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wishlist
        fields = "__all__"
        read_only_fields = ["user"]
        

class DealSerializer(serializers.ModelSerializer):

    class Meta:
        model = Deal
        fields = '__all__'
        
class ContactThreadSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactThread
        fields = '__all__'