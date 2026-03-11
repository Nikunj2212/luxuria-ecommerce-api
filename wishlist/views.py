from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from products.models import Product
from .models import Wishlist
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404    


@login_required(login_url='login')
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    wishlist_item = Wishlist.objects.filter(
        user=request.user,
        product=product
    )

    if wishlist_item.exists():
        wishlist_item.delete()
        status = "removed"
    else:
        Wishlist.objects.create(
            user=request.user,
            product=product
        )
        status = "added"

    count = Wishlist.objects.filter(user=request.user).count()

    return JsonResponse({
        "status": status,
        "wishlist_count": count
    })
    
    
@login_required(login_url='login')
def wishlist_page(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related("product")

    return render(request, "wishlist/wishlist.html", {
        "wishlist_items": wishlist_items
    })
    
    
@login_required(login_url='login')
def remove_from_wishlist(request, product_id):
    wishlist_item = get_object_or_404(
        Wishlist,
        user=request.user,
        product_id=product_id
    )
    wishlist_item.delete()
    messages.success(request, "Removed from wishlist")
    return redirect("wishlist")