from rest_framework import generics,filters
from products.models import Product
from .serializers import ProductSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import CartSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from carts.models import Cart
from .serializers import AddToCartSerializer    
from carts.models import Order, OrderItem
from .serializers import OrderSerializer
from .serializers import CreateOrderSerializer
from .serializers import OrderDetailSerializer
from rest_framework.generics import RetrieveAPIView
from rest_framework.generics import ListAPIView
from products.models import Category
from .serializers import CategorySerializer
from products.models import SubCategory
from .serializers import SubCategorySerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView
from .serializers import ProductReviewSerializer
from products.models import ProductReview
from wishlist.models import Wishlist
from rest_framework.generics import ListAPIView
from .serializers import WishlistSerializer
from dashboard.models import Deal
from .serializers import DealSerializer
from django.db.models import Avg
from rest_framework.generics import ListCreateAPIView
from contact.models import ContactThread
from .serializers import ContactThreadSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
import uuid

class ProductListAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'subcategory']
    search_fields = ['name', 'description']

    def get_queryset(self):
        queryset = Product.objects.all()

        price_min = self.request.query_params.get('price_min')
        price_max = self.request.query_params.get('price_max')

        if price_min:
            queryset = queryset.filter(price__gte=price_min)

        if price_max:
            queryset = queryset.filter(price__lte=price_max)
            
            sort = self.request.query_params.get("sort")

        if sort:
            queryset = queryset.order_by(sort)

        return queryset
    
    
class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    
class CartListAPIView(generics.ListAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
class AddToCartAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = AddToCartSerializer(data=request.data)

        if serializer.is_valid():

            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data.get('quantity', 1)

            product = get_object_or_404(Product, id=product_id)

            cart_item, created = Cart.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'quantity': quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return Response({
                "message": "Product added to cart successfully"
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class UpdateCartAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request):

        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity")

        try:
            cart_item = Cart.objects.get(
                user=request.user,
                product_id=product_id
            )

            cart_item.quantity = quantity
            cart_item.save()

            return Response({
                "message": "Cart updated successfully"
            })

        except Cart.DoesNotExist:

            return Response({
                "error": "Item not found in cart"
            })
            
class RemoveCartAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request):

        product_id = request.data.get("product_id")

        try:
            cart_item = Cart.objects.get(
                user=request.user,
                product_id=product_id
            )

            cart_item.delete()

            return Response({
                "message": "Item removed from cart"
            })

        except Cart.DoesNotExist:

            return Response({
                "error": "Item not found in cart"
            })
            
class CreateOrderAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = CreateOrderSerializer(data=request.data)

        if serializer.is_valid():

            cart_items = Cart.objects.filter(user=request.user)

            if not cart_items.exists():
                return Response({
                    "error": "Cart is empty"
                }, status=status.HTTP_400_BAD_REQUEST)

            total_amount = 0

            for item in cart_items:
                total_amount += item.product.price * item.quantity

            # 🔥 Generate unique order id
            order_id = str(uuid.uuid4())[:8]

            order = Order.objects.create(

                order_id=str(uuid.uuid4())[:8],

                user=request.user,
                customer_name=serializer.validated_data['customer_name'],
                customer_email=serializer.validated_data['customer_email'],
                phone=serializer.validated_data['phone'],
                address=serializer.validated_data['address'],
                city=serializer.validated_data['city'],
                pincode=serializer.validated_data['pincode'],
                payment_method=serializer.validated_data['payment_method'],
                total_amount=total_amount
            )

            for item in cart_items:

                OrderItem.objects.create(

                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    price=item.product.price

                )

            # 🔥 Clear cart
            cart_items.delete()

            return Response({
                "message": "Order placed successfully",
                "order_id": order.order_id
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
class MyOrdersAPIView(generics.ListAPIView):

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
    
class OrderDetailAPIView(RetrieveAPIView):

    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
class CategoryListAPIView(ListAPIView):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
class SubCategoryListAPIView(ListAPIView):

    serializer_class = SubCategorySerializer

    def get_queryset(self):
        category_id = self.request.query_params.get('category')
        return SubCategory.objects.filter(category_id=category_id)
    
class ProductReviewCreateAPIView(CreateAPIView):

    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        

class ProductReviewListAPIView(ListAPIView):

    serializer_class = ProductReviewSerializer

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return ProductReview.objects.filter(product_id=product_id)
    
class AddToWishlistAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        product_id = request.data.get("product_id")

        product = get_object_or_404(Product, id=product_id)

        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )

        if created:
            return Response({
                "message": "Product added to wishlist"
            })

        return Response({
            "message": "Product already in wishlist"
        })
        
    
class MyWishlistAPIView(ListAPIView):

    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)
    
class RemoveWishlistAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request):

        product_id = request.data.get("product_id")

        Wishlist.objects.filter(
            user=request.user,
            product_id=product_id
        ).delete()

        return Response({
            "message": "Product removed from wishlist"
        })
        
class TopRatedProductsAPIView(ListAPIView):

    serializer_class = ProductSerializer

    def get_queryset(self):

        return Product.objects.annotate(
            average_rating=Avg('reviews__rating')
        ).order_by('-average_rating')[:10]
        
        
class DealListAPIView(ListAPIView):

    queryset = Deal.objects.all()
    serializer_class = DealSerializer
    
class ContactThreadAPIView(ListCreateAPIView):

    serializer_class = ContactThreadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ContactThread.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
class CartSummaryAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        cart_items = Cart.objects.filter(user=request.user)

        total_items = sum(item.quantity for item in cart_items)
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        return Response({
            "items": total_items,
            "total_price": total_price
        })
        
class RelatedProductsAPIView(ListAPIView):

    serializer_class = ProductSerializer

    def get_queryset(self):

        product_id = self.kwargs["pk"]

        product = Product.objects.get(id=product_id)

        return Product.objects.filter(
            category=product.category
        ).exclude(id=product_id)[:6]
        
class OrderTrackingAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):

        try:
            order = Order.objects.get(
                order_id=order_id,
                user=request.user
            )

            return Response({
                "order_id": order.order_id,
                "status": order.status,
                "created_at": order.created_at
            })

        except Order.DoesNotExist:

            return Response({
                "error": "Order not found"
            })
            
class TrendingProductsAPIView(ListAPIView):

    serializer_class = ProductSerializer

    def get_queryset(self):

        return Product.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).order_by('-avg_rating')[:8]
        
        
class RecommendedProductsAPIView(ListAPIView):

    serializer_class = ProductSerializer

    def get_queryset(self):

        product_id = self.kwargs['pk']

        product = Product.objects.get(id=product_id)

        return Product.objects.filter(
            category=product.category
        ).exclude(id=product_id)[:6]