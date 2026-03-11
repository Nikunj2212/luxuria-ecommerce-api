from django.urls import path
from . import views
from .views import add_review

app_name = 'products'

urlpatterns = [
    path('', views.products_list, name='product_list'),
    path('search/', views.search, name='search'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('subcategory/<int:id>/',views.subcategory_products,name='subcategory_products'),
    path('load-subcategories/', views.load_subcategories, name='ajax_load_subcategories'),
    path('categories/', views.category_list, name='category_list'),
    path('products/category/<int:category_id>/', views.category_products, name='category_products'),
    path('category/<int:id>/subcategories/',views.category_subcategories,name='category_subcategories'),
    path('review/add/<int:product_id>/', add_review, name='add_review'),
    path("search-suggestions/", views.search_suggestions, name="search_suggestions"),

    

]
