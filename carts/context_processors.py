from .models import *
from django.contrib.auth.decorators import login_required
from django.db.models import Sum


def cart_item_count(request):

    if request.user.is_authenticated:
        count = Cart.objects.filter(user=request.user).aggregate(
            total=Sum("quantity")
        )["total"] or 0
    else:
        count = 0   # 🔥 IMPORTANT LINE

    return {
        "cart_item_count": count
    }