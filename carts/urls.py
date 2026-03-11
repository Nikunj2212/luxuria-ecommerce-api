from django.urls import path
from . import views

app_name = "carts"

urlpatterns = [
    # CART VIEW
    path('', views.cart_detail, name='cart'),

    # CART ACTIONS
    path("add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("increase/<int:id>/", views.increase_qty, name="increase_qty"),
    path("decrease/<int:id>/", views.decrease_qty, name="decrease_qty"),
    path("remove/<int:id>/", views.remove_from_cart, name="remove_from_cart"),

    # CHECKOUT + PAYMENT
    path("checkout/", views.checkout, name="checkout"),
    path("payment-method/", views.payment_method, name="payment_method"),
    path("invoice/<str:order_id>/", views.invoice_view, name="invoice"),
    path("payment/", views.payment_gateway, name="payment"),
    path("process/", views.process_payment, name="process_payment"),
    path("success/<str:order_id>/", views.payment_success, name="payment_success"),
    path("payment-gateway/", views.payment_gateway, name="payment_gateway"),
    path("invoice/", views.invoice_view, name="invoice"),
    path("processing/", views.processing, name="processing"),
    path("clear/", views.clear_cart, name="clear_cart"),
    path("buy-now/<int:product_id>/", views.buy_now, name="buy_now"),
    

]
