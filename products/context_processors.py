from .models import Category

def categories_processor(request):
    return {
        "categories": Category.objects.all()
    }
    
    
def cart_count(request):
    cart = request.session.get("cart", {})
    return {
        "cart_item_count": sum(cart.values())
    }