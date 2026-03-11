from django.shortcuts import render, redirect
from .models import ContactMessage
from .models import ContactMessage
from django.shortcuts import render, redirect
from products.models import Product, Category,SubCategory
from django.utils import timezone
from .models import HomeSlider
from dashboard.models import Deal
from django.utils import timezone
from wishlist.models import Wishlist
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from carts.models import Cart 




def home(request):
    sliders = HomeSlider.objects.filter(is_active=True)
    categories = Category.objects.all()
    products = Product.objects.all().order_by('-id')

    deals_of_day = Deal.objects.filter(
        expiry__gt=timezone.now()
    ).select_related("product")

    home_sections = []

    for category in categories:
        category_products = Product.objects.filter(
            category=category
        ).order_by('-id')

        if category_products.exists():
            home_sections.append({
                "subcategory": category,
                "products": category_products,
            })

    # ✅ Wishlist
    if request.user.is_authenticated:
        wishlist_products = Wishlist.objects.filter(
            user=request.user
        ).values_list("product_id", flat=True)

        # ✅ NEW: Cart Products
        cart_products = Cart.objects.filter(
            user=request.user
        ).values_list("product_id", flat=True)
    else:
        wishlist_products = []
        cart_products = []

    return render(request, "pages/home.html", {
        "sliders": sliders,
        "categories": categories,
        "deals_of_day": deals_of_day,
        "home_sections": home_sections,
        "wishlist_products": wishlist_products,
        "cart_products": cart_products,   # 🔥 IMPORTANT
        "products": products,
    })

    
def login_view(request):
    return render(request, 'accounts/login.html')


def about(request):
    return render(request, 'pages/about.html')


def contact(request):
    if request.method == "POST":
        ContactMessage.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            message=request.POST.get('message')
        )
        return redirect('contact_success')

    return render(request, 'pages/contact.html')

def collection(request):
    products = Product.objects.all()

    if request.user.is_authenticated:
        cart_products = Cart.objects.filter(
            user=request.user
        ).values_list("product_id", flat=True)
    else:
        cart_products = []

    return render(request, 'collection.html', {
        'products': products,
        'cart_products': cart_products,
    })


def contact_success(request):
    return render(request, 'pages/contact_success.html')




