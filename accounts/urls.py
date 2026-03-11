from django.urls import path
from . import views
from .views import ticket_detail
from .views import signup_view, login_view, complete_profile

app_name = "accounts"

urlpatterns = [
    path('login/', login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('complete-profile/', views.complete_profile, name='complete_profile'),
    path('orders/', views.my_orders, name='my_orders'),
    path('orders/track/<uuid:order_id>/', views.track_order, name='track_order'),
    path('profile/', views.profile, name='profile'),
    path('edit-address/', views.edit_address, name='edit_address'), 
    path('download-invoice/', views.profile, name='download_invoice'),
    path('help/', views.help_center, name='help_center'),
    path('logout/', views.user_logout, name='logout'),
    path('ticket/<int:thread_id>/', ticket_detail, name='ticket_detail'),
    path("invoice/<uuid:order_id>/",views.download_invoice,name="download_invoice"),
    path('change-password/', views.change_password, name='change_password'),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("ajax/send-otp/", views.send_otp),
    path("ajax/verify-otp/", views.verify_otp),
    path("ajax/reset-password/", views.reset_password),
    path("wishlist/", views.wishlist, name="wishlist"),

]
