from django.urls import path
from .views import ProductListAPIView,ProductDetailAPIView
from .views import CartListAPIView,CategoryListAPIView,SubCategoryListAPIView
from .views import AddToCartAPIView,CreateOrderAPIView
from .views import UpdateCartAPIView,RemoveCartAPIView,ProductReviewListAPIView,RecommendedProductsAPIView
from .views import MyOrdersAPIView,OrderDetailAPIView,ProductReviewCreateAPIView,TrendingProductsAPIView
from .views import AddToWishlistAPIView, MyWishlistAPIView, RemoveWishlistAPIView,RelatedProductsAPIView
from .views import TopRatedProductsAPIView,DealListAPIView,ContactThreadAPIView,CartSummaryAPIView,OrderTrackingAPIView



urlpatterns = [
    path('products/', ProductListAPIView.as_view(), name='api-products'),
    path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='api-product-detail'),
    path('cart/', CartListAPIView.as_view(), name='cart-list'),
    path('cart/add/', AddToCartAPIView.as_view(), name='add-to-cart'),
    path('cart/update/', UpdateCartAPIView.as_view(), name='update-cart'),
    path('cart/remove/', RemoveCartAPIView.as_view(), name='remove-cart'),
    path('order/create/', CreateOrderAPIView.as_view(), name='create-order'),
    path('my-orders/', MyOrdersAPIView.as_view(), name='my-orders'),
    path('order/<int:pk>/', OrderDetailAPIView.as_view(), name='order-detail'),
    path('categories/', CategoryListAPIView.as_view(), name='categories'),
    path('subcategories/', SubCategoryListAPIView.as_view(), name='subcategories'),
    path('product/review/', ProductReviewCreateAPIView.as_view(), name='product-review'),
    path('product/<int:product_id>/reviews/', ProductReviewListAPIView.as_view(), name='product-reviews'),
    path('wishlist/add/', AddToWishlistAPIView.as_view(), name='wishlist-add'),
    path('wishlist/', MyWishlistAPIView.as_view(), name='my-wishlist'),
    path('wishlist/remove/', RemoveWishlistAPIView.as_view(), name='wishlist-remove'),
    path('top-products/', TopRatedProductsAPIView.as_view(), name='top-products'),
    path('deals/', DealListAPIView.as_view(), name='deals'),
    path('contact/', ContactThreadAPIView.as_view(), name='contact-api'),
    path('cart/summary/', CartSummaryAPIView.as_view(), name='cart-summary'),
    path('products/<int:pk>/related/', RelatedProductsAPIView.as_view(), name='related-products'),
    path('order/track/<str:order_id>/',OrderTrackingAPIView.as_view(),name='order-tracking'),
    path('trending-products/', TrendingProductsAPIView.as_view(), name='trending-products'),
    path('products/<int:pk>/recommendations/',RecommendedProductsAPIView.as_view(),name='recommended-products'),
    
]