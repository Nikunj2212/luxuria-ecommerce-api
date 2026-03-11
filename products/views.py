from .models import Product, ProductReview
from .forms import ReviewForm
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Product, Category, SubCategory
from django.utils import timezone
from dashboard.models import Deal
from .models import Product, ProductReview
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from wishlist.models import Wishlist 


def home(request):
    return render(request, 'products/home.html')


def products_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    cat_id = request.GET.get("cat")
    sub_id = request.GET.get("sub")

    # If category selected → show subcategories
    if cat_id and not sub_id:
        subcategories = SubCategory.objects.filter(category_id=cat_id)

        return render(request, "products/products_list.html", {
            "categories": categories,
            "subcategories": subcategories,
            "products": [],
        })

    # If subcategory selected → show products
    if sub_id:
        products = Product.objects.filter(subcategory_id=sub_id)

    return render(request, "products/products_list.html", {
        "categories": categories,
        "subcategories": None,
        "products": products,
    })

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    deal = Deal.objects.filter(
        product=product,
        expiry__gt=timezone.now()
    ).first()

    discounted_price = deal.discounted_price if deal else None

    similar_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]

    reviews = product.reviews.all()
    avg_rating = product.reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    avg_rating = round(avg_rating, 1)

    # ✅ ADD THIS
    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(
            user=request.user,
            product=product
        ).exists()

    return render(request, "products/product_detail.html", {
        "product": product,
        "deal": deal,
        "discounted_price": discounted_price,
        "reviews": reviews,
        "avg_rating": avg_rating,
        "similar_products": similar_products,
        "is_wishlisted": is_wishlisted,   # 👈 important
    })

def search(request):
    q = request.GET.get("q","")
    results = Product.objects.filter(name__icontains=q)[:6]
    return JsonResponse({
        "results":[
            {"id":p.id,"name":p.name} for p in results
        ]
    })


def search_suggestions(request):
    query = request.GET.get("q")
    results = []

    if query:

        # 🔹 Products
        products = Product.objects.filter(name__icontains=query)[:5]
        for product in products:
            results.append({
                "type": "product",
                "name": product.name,
                "url": f"/products/product/{product.id}/",
                "price": str(product.price),
                "image": product.image.url if product.image else ""
            })

        # 🔹 Categories
        categories = Category.objects.filter(name__icontains=query)[:3]
        for cat in categories:
            results.append({
                "type": "category",
                "name": cat.name,
                "url": f"/products/products/category/{cat.id}/",
                "image": cat.image.url if cat.image else ""
            })

        # 🔹 Subcategories
        subcategories = SubCategory.objects.filter(name__icontains=query)[:3]
        for sub in subcategories:
            results.append({
                "type": "subcategory",
                "name": sub.name,
                "url": f"/products/subcategory/{sub.id}/",
                "image": sub.image.url if sub.image else ""
            })

    return JsonResponse(results, safe=False)


# ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐
# CART ACTIONS → Redirect to CARTS APP
# ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐

def add_to_cart(request, product_id):
    cart = request.session.get("cart", {})

    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session["cart"] = cart

    return redirect("carts:cart")


def decrease_qty(request, product_id):
    cart = request.session.get("cart", {})

    if str(product_id) in cart:
        if cart[str(product_id)] > 1:
            cart[str(product_id)] -= 1
        else:
            del cart[str(product_id)]

    request.session["cart"] = cart
    return redirect("carts:cart")


def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    cart.pop(str(product_id), None)
    request.session["cart"] = cart
    return redirect("carts:cart")


# ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐
# AJAX LOAD SUBCATEGORY
# ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐

def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    subcategories = SubCategory.objects.filter(category=category)

    selected_price = request.GET.get('price')

    if selected_price:
        if selected_price == '0-10000':
            products = products.filter(price__gte=0, price__lte=10000)
        elif selected_price == '10000-20000':
            products = products.filter(price__gte=10000, price__lte=20000)
        elif selected_price == '20000-30000':
            products = products.filter(price__gte=20000, price__lte=30000)
        elif selected_price == '30000+':
            products = products.filter(price__gte=30000)

    # ✅ IMPORTANT — Wishlist IDs fetch karo
    wishlist_products = []

    if request.user.is_authenticated:
        wishlist_products = Wishlist.objects.filter(
            user=request.user
        ).values_list("product_id", flat=True)

    return render(request, 'products/category_products.html', {
        'category': category,
        'products': products,
        'subcategories': subcategories,
        'selected_price': selected_price,
        'wishlist_products': wishlist_products,  # 👈 add this
    })





def category_subcategories(request, id):
    category = get_object_or_404(Category, id=id)
    subcategories = SubCategory.objects.filter(category=category)

    return render(request,'products/subcategories.html',{
        'category': category,
        'subcategories': subcategories
    })


def subcategory_products(request, id):
    subcategory = SubCategory.objects.get(id=id)
    products = Product.objects.filter(subcategory=subcategory)

    price_range = request.GET.get('price')

    if price_range == "0-10000":
        products = products.filter(price__gte=0, price__lte=10000)
    elif price_range == "10000-20000":
        products = products.filter(price__gte=10000, price__lte=20000)
    elif price_range == "20000-30000":
        products = products.filter(price__gte=20000, price__lte=30000)
    elif price_range == "30000+":
        products = products.filter(price__gte=30000)

    context = {
        'products': products,
        'subcategory': subcategory,
        'selected_price': price_range,
    }

    return render(request, 'products/subcategory_products.html', context)


    
def load_subcategories(request):
    category_id = request.GET.get('category_id')

    subcategories = SubCategory.objects.filter(
        category_id=category_id
    ).values('id', 'name')

    return JsonResponse(list(subcategories), safe=False)


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'products/category_list.html', {
        'categories': categories
    })



@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        rating = request.POST.get("rating")
        review_text = request.POST.get("review")  # textarea name

        ProductReview.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            review=review_text   # ✅ yaha review use karo
        )

    return redirect('products:product_detail', id=product.id)