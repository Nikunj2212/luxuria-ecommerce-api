from contact.views import close_thread
from django.urls import path
from . import views
from contact.views import thread_list

app_name = "dashboard"

urlpatterns = [

        # HOME
        path("", views.dashboard_home, name="dashboard_home"),

        # USERS
        path("users/", views.users_report, name="users_report"),
        path("create-admin/", views.create_dashboard_admin, name="dashboard_create_admin"),
        
       path('customers/delete/<int:user_id>/', views.delete_customer, name='delete_customer'),

        # CATEGORY + SUBCATEGORY
        path("categories/", views.category_list, name='category_list'),
        path("category/add/", views.add_category, name="add_category"),
        path("category/edit/<int:pk>/", views.edit_category, name='edit_category'),
        path("category/delete/<int:pk>/", views.delete_category, name="delete_category"),

        path('subcategories/', views.subcategory_list, name='subcategory_list'),
        path("subcategory/add/", views.subcategory_add, name="subcategory_add"),
        path("subcategory/edit/<int:pk>/", views.subcategory_edit, name='subcategory_edit'),
        path("subcategory/delete/<int:id>/", views.delete_subcategory, name='delete_subcategory'),

        # PRODUCTS
        path("products/", views.products_list, name="products_list"),
        path("product/add/", views.add_product, name="add_product"),
        path("product/edit/<int:pk>/", views.edit_product, name="edit_product"),
        path("product/delete/<int:pk>/", views.delete_product, name="delete_product"),

        # OFFERS
        path("offers/", views.offers_list, name="offers_list"),
        path("offers/add/", views.add_offer, name="add_offer"),
        path("offers/edit/<int:pk>/", views.edit_offer, name="edit_offer"),
        path("offers/delete/<int:pk>/", views.delete_offer, name="delete_offer"),

        # INVENTORY + ORDERS + CUSTOMERS
        path('inventory/', views.inventory, name='inventory'),
        path("orders/", views.orders_list, name="orders_list"),
        path("orders/update/<str:order_id>/", views.update_order_status, name="update_order_status"),
        path("customers/", views.customers_list, name="customers_list"),

        # NEWSLETTER + OLD CONTACT
        path("messages/", views.contact_messages, name="messages_list"),
        path("messages/reply/<int:id>/", views.reply_message, name="reply_message"),
        path("messages/send-newsletter/", views.send_newsletter, name="send_newsletter"),

        # ⭐ SUPPORT TICKETS ⭐ (CORRECT
        path('support/', thread_list, name='dashboard_support'),
        path('support/<int:thread_id>/',views.support_detail,name='dashboard_support_detail'),

        # AUTH
        path("login/", views.dashboard_login, name="dashboard_login"),
        path("logout/", views.dashboard_logout, name="dashboard_logout"),
        path('register/', views.dashboard_register, name='dashboard_register'),
        path('support/<int:thread_id>/close/', views.close_thread, name="dashboard_support_close"),
        path("support/<int:thread_id>/delete/",views.delete_support_ticket,name="dashboard_support_delete"),
        path('sliders/', views.slider_list, name='slider_list'),
        path('sliders/add/', views.slider_add, name='slider_add'),
        path('sliders/edit/<int:id>/', views.slider_edit, name='slider_edit'),
        path('deals/', views.deals_list, name='deals'),
        path("deals/edit/<int:id>/", views.edit_deal, name="edit_deal"),
        path('deals/', views.deals_list, name='deals_list'),
        path('sliders/delete/<int:id>/', views.slider_delete, name='slider_delete'),
        path("deals/remove/<int:id>/", views.remove_deal, name="remove_deal"),
        path("deals/add/", views.add_deal, name="add_deal"),
        path("deals/delete/<int:id>/", views.delete_deal, name="delete_deal"),
        path("ajax/subcategories/", views.get_subcategories, name="get_subcategories"),
        path("ajax/products/", views.get_products, name="get_products"),


    ]
