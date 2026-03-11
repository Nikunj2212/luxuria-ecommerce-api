from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
User = get_user_model()
from django.db.models import Sum
from products.models import Category, SubCategory
from products.models import Product, Category
from carts.models import Order
from accounts.models import Address
from contact.models import ContactMessage
from django.core.mail import send_mail
from django.conf import settings
from carts.models import Order, OrderItem 
from datetime import timedelta
from django.utils import timezone
from products.models import Offer
from contact.models import ContactThread, ContactMessage
from .decorators import dashboard_login_required
from django.http import HttpResponse
from pages.models import HomeSlider
from .forms import HomeSliderForm
from django.utils.dateparse import parse_datetime
from .models import Deal
from django.http import JsonResponse
from products.models import Offer
from datetime import datetime
from accounts.models import User
from .models import DashboardAdmin
from decimal import Decimal

# =====================
# ADMIN CHECK
# =====================
def admin_only(user):
    return user.is_authenticated and user.is_staff


# =====================
# DASHBOARD LOGIN
# =====================
def dashboard_login(request):
    if request.session.get("dashboard_is_admin"):
        return redirect("dashboard:dashboard_home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        attempts = request.session.get("login_attempts", 0)
        if attempts >= 5:
            messages.error(request, "Too many attempts. Try later.")
            return render(request, "dashboard/login.html")

        try:
            admin = DashboardAdmin.objects.get(username=username)
        except DashboardAdmin.DoesNotExist:
            messages.error(request, "Admin not found")
            return render(request, "dashboard/login.html")

        if not admin.check_password(password):
            request.session["login_attempts"] = attempts + 1
            messages.error(request, "Wrong password")
            return render(request, "dashboard/login.html")

        request.session.flush()
        request.session["dashboard_admin_id"] = admin.id
        request.session["dashboard_is_admin"] = True
        request.session.set_expiry(1800)

        return redirect("dashboard:dashboard_home")

    return render(request, "dashboard/login.html")






@dashboard_login_required
def dashboard_logout(request):
    request.session.pop("dashboard_user_id", None)
    request.session.pop("dashboard_is_admin", None)
    return redirect("dashboard:dashboard_login")
# =====================
# DASHBOARD HOME
# =====================
@dashboard_login_required
def dashboard_home(request):
    # 🚩 Total KPIs
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_users = User.objects.count()

    total_revenue = Order.objects.filter(status="PAID").aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    # 🚩 Today revenue
    today = timezone.now().date()
    today_sales = Order.objects.filter(
        status="PAID",
        created_at__date=today
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # 🚩 Last 7 days graph
    graph_labels = []
    graph_values = []

    for i in range(7):
        day = today - timedelta(days=i)
        graph_labels.append(day.strftime("%d %b"))
        total = Order.objects.filter(created_at__date=day).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        graph_values.append(float(total))

    graph_labels.reverse()
    graph_values.reverse()

    # 🚩 Top selling products
    top_products = OrderItem.objects.values('product_name').annotate(
        sold=Sum('quantity')
    ).order_by('-sold')[:5]

    return render(request, "dashboard/dashboard_home.html", {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_users": total_users,
        "total_revenue": total_revenue,
        "today_sales": today_sales,
        "graph_labels": graph_labels,
        "graph_values": graph_values,
        "top_products": top_products,
    })

# =====================
# USERS REPORT
# =====================
@dashboard_login_required
def users_report(request):
    users = User.objects.filter(is_staff=False)

    data = []

    for user in users:
        address = Address.objects.filter(user=user).first()
        orders = Order.objects.filter(user=user)

        total_spent = orders.aggregate(
            total=Sum("total_amount")
        )["total"] or 0

        data.append({
            "user": user,
            "address": address,
            "orders_count": orders.count(),
            "total_spent": total_spent,
            "last_login": user.last_login,
            "joined": user.date_joined,
        })

    return render(request, "dashboard/users_report.html", {
        "data": data
    })
# =====================
# DELETE USER
# =====================
@dashboard_login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user == request.user:
        messages.error(request, "You cannot delete yourself")
        return redirect("dashboard:users_report")

    user.delete()
    messages.success(request, "User deleted successfully")
    return redirect("dashboard:users_report")


# =====================
# CATEGORY
# =====================
@dashboard_login_required
def add_category(request):
    if request.method == "POST":
        name = request.POST.get("name")
        image = request.FILES.get("image")

        if not name:
            messages.error(request, "Category name is required")
            return redirect("dashboard:add_category")

        if Category.objects.filter(name__iexact=name).exists():
            messages.warning(request, "Category already exists")
            return redirect("dashboard:add_category")

        # SAVE IMAGE HERE
        Category.objects.create(
            name=name,
            image=image
        )

        messages.success(request, "Category added successfully")
        return redirect("dashboard:category_list")

    return render(request, "dashboard/add_category.html")

@dashboard_login_required
def delete_category(request, pk):
    get_object_or_404(Category, pk=pk).delete()
    messages.success(request, "Category deleted successfully")
    return redirect("dashboard:category_list")


# =====================
# PRODUCT
# =====================

@dashboard_login_required
def add_product(request):
    if request.method == "POST":
        Product.objects.create(
            name=request.POST.get("name"),
            price=request.POST.get("price"),
            description=request.POST.get("description"),
            category_id=request.POST.get("category"),
            subcategory_id=request.POST.get("subcategory"),  # 🌟 NEW
            image=request.FILES.get("image")
        )

        messages.success(request, "Product added successfully")
        return redirect('dashboard:products_list')

    return render(request, "dashboard/add_product.html", {
        "categories": Category.objects.all(),
        "subcategories": SubCategory.objects.all(),  # 🌟 NEW
    })

@dashboard_login_required
def delete_product(request, pk):
    get_object_or_404(Product, pk=pk).delete()
    messages.success(request, "Product deleted successfully")
    return redirect('dashboard:products_list')




def create_dashboard_admin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if DashboardAdmin.objects.filter(username=username).exists():
            messages.error(request, "Admin name already exists")
        else:
            admin = DashboardAdmin(username=username)
            admin.set_password(password)
            admin.save()
            messages.success(request, "Admin created")
            return redirect("dashboard:dashboard_login")

    return render(request, "dashboard/create_admin.html")


@dashboard_login_required
def contact_messages(request):
    messages = ContactMessage.objects.filter(
        thread__isnull=False
    ).select_related("thread").order_by("-created_at")

    return render(request, "dashboard/messages_list.html", {
        "messages": messages
    })

@dashboard_login_required
def subcategory_add(request):
    categories = Category.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        cat_id = request.POST.get("category")
        category = Category.objects.get(id=cat_id)

        SubCategory.objects.create(
            category=category,
            name=name,
            image=request.FILES.get("image")
        )

        return redirect("dashboard:subcategory_list") 

    return render(request, "dashboard/subcategory.html", {
        "categories": categories
    })
    
    
@dashboard_login_required
def delete_subcategory(request, id):
    sub = get_object_or_404(SubCategory, id=id)
    sub.delete()
    return redirect('dashboard:subcategory_list')



# ⭐ View All Orders
@dashboard_login_required
def orders_list(request):
    search = request.GET.get("search")

    orders = Order.objects.all().order_by("-created_at")

    if search:
        orders = orders.filter(order_id__icontains=search)

    return render(request, "dashboard/orders_list.html", {
        "orders": orders,
        "search": search,
    })


# ⭐ Update Order Status
@dashboard_login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)

    if request.method == "POST":
        order.status = request.POST.get("status")
        order.save()
        messages.success(request, "Order status updated")
        return redirect("dashboard:orders_list")

    return render(request, "dashboard/update_order.html", {
        "order": order
    })


@dashboard_login_required
def customers_list(request):
    customers = User.objects.filter(is_staff=False).order_by('-date_joined')

    data = []
    for user in customers:
        address = Address.objects.filter(user=user).first()

        data.append({
            "user": user,
            "address": address
        })

    return render(request, "dashboard/customers_list.html", {
        "customers": data
    })


@dashboard_login_required    
def delete_customer(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        user.delete()
    return redirect('dashboard:customers_list')
    
@dashboard_login_required
def support_list(request):
    threads = ContactThread.objects.order_by('-created_at')
    return render(request, "dashboard/support_list.html", {
        "threads": threads
    })


@dashboard_login_required
def support_detail(request, thread_id):
    thread = get_object_or_404(ContactThread, id=thread_id)
    msgs = thread.messages.all().order_by("created_at")

    if request.method == "POST":
        if thread.status == "closed":
            return redirect("dashboard:dashboard_support_detail", thread_id=thread_id)

        reply = request.POST.get("message")   # ✅ FIX HERE

        if reply:
            ContactMessage.objects.create(
                thread=thread,
                sender="admin",
                message=reply
            )

        return redirect("dashboard:dashboard_support_detail", thread_id=thread_id)

    return render(request, "dashboard/support_detail.html", {
        "thread": thread,
        "messages": msgs
    })


@dashboard_login_required
def messages_list(request):
    threads = ContactThread.objects.all().order_by('-created_at')
    return render(request, 'dashboard/messages_list.html', {'threads': threads})

@dashboard_login_required
def reply_message(request, id):
    msg = get_object_or_404(ContactMessage, id=id)

    if request.method == "POST":
        reply = request.POST["reply"]
        msg.reply = reply
        msg.is_replied = True
        msg.save()

        # SEND EMAIL BACK TO USER
        send_mail(
            "Reply from Luxuria",
            reply,
            settings.EMAIL_HOST_USER,
            [msg.email],
            fail_silently=False
        )

        return redirect("dashboard:messages_list")

    return render(request, "dashboard/message_reply.html", {"msg": msg})


@dashboard_login_required
def send_newsletter(request):
    if request.method == "POST":
        content = request.POST["content"]
        emails = ContactMessage.objects.values_list("email", flat=True).distinct()

        for email in emails:
            send_mail(
                "Luxuria Newsletter",
                content,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False
            )

        return redirect("dashboard:messages_list")

    return render(request, "dashboard/newsletter_form.html")


@dashboard_login_required
def add_offer(request):
    categories = Category.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        discount = request.POST.get("discount")
        product_id = request.POST.get("product")

        # checkbox safe handling
        active = True if request.POST.get("is_active") == "on" else False

        # 1️⃣ create offer
        offer = Offer.objects.create(
            name=name,
            discount=discount,
            active=active
        )

        # 2️⃣ attach offer to product (ONLY if selected)
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                product.offer = offer
                product.save()
            except Product.DoesNotExist:
                pass

        return redirect("dashboard:offers_list")

    return render(request, "dashboard/add_offer.html", {
        "categories": categories
    })

    
def get_subcategories(request):
    category_id = request.GET.get("category_id")
    subcategories = SubCategory.objects.filter(category_id=category_id)
    data = [{"id": s.id, "name": s.name} for s in subcategories]
    return JsonResponse(data, safe=False)


def get_products(request):
    subcategory_id = request.GET.get("subcategory_id")
    products = Product.objects.filter(subcategory_id=subcategory_id)
    data = [{"id": p.id, "name": p.name} for p in products]
    return JsonResponse(data, safe=False)



@dashboard_login_required
def offers_list(request):
    offers = Offer.objects.all()
    return render(request, "dashboard/offers_list.html", {"offers": offers})

@dashboard_login_required
def edit_offer(request, pk):
    offer = get_object_or_404(Offer, pk=pk)

    if request.method == "POST":
        offer.name = request.POST["name"]
        offer.discount = request.POST["discount"]
        offer.active = 'active' in request.POST
        offer.save()

        messages.success(request, "Offer updated!")
        return redirect("dashboard:offers_list")

    return render(request, "dashboard/edit_offer.html", {"offer": offer})

@dashboard_login_required
def delete_offer(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    offer.delete()
    messages.success(request, "Offer deleted!")
    return redirect("dashboard:offers_list")


@dashboard_login_required
def products_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    category_id = request.GET.get("category")
    subcategory_id = request.GET.get("subcategory")

    # 👇 CATEGORY FILTER
    if category_id:
        products = products.filter(category_id=category_id)
        subcategories = SubCategory.objects.filter(category_id=category_id)
    else:
        subcategories = SubCategory.objects.none()  # ❌ sab mat dikhao

    # 👇 SUBCATEGORY FILTER
    if subcategory_id:
        products = products.filter(subcategory_id=subcategory_id)

    context = {
        "products": products,
        "categories": categories,
        "subcategories": subcategories,
        "selected_category": category_id,
        "selected_subcategory": subcategory_id,
    }

    return render(request, "dashboard/products_list.html", context)



@dashboard_login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product.name = request.POST["name"]
        product.price = request.POST["price"]
        product.description = request.POST["description"]
        product.category_id = request.POST["category"]
        
        # ❗ If Subcategory exist
        if "subcategory" in request.POST:
            product.subcategory_id = request.POST["subcategory"]

        if "offer" in request.POST:
            product.offer_id = request.POST["offer"]

        # ❗ Update image only if new file uploaded
        if "image" in request.FILES:
            product.image = request.FILES["image"]

        product.save()
        messages.success(request, "Product updated successfully!")
        return redirect('dashboard:products_list')

    return render(request, "dashboard/edit_product.html", {
        "product": product,
        "categories": Category.objects.all(),
        "subcategories": SubCategory.objects.all(),
        "offers": Offer.objects.all()
    })
    
@dashboard_login_required    
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'dashboard/category_list.html', {'categories': categories})


@dashboard_login_required
def subcategory_list(request):
    categories = Category.objects.all()

    selected_category = request.GET.get("category")

    subcategories = SubCategory.objects.select_related("category")

    if selected_category:
        subcategories = subcategories.filter(category_id=selected_category)

    return render(request, "dashboard/subcategory_list.html", {
        "subcategories": subcategories,
        "categories": categories,
        "selected_category": selected_category,
    })


@dashboard_login_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        category.name = request.POST.get("name")
        if "image" in request.FILES:
            category.image = request.FILES["image"]
        category.save()
        return redirect('dashboard:category_list')

    return render(request, 'dashboard/edit_category.html', {'category': category})

@dashboard_login_required
def subcategory_edit(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)
    categories = Category.objects.all()

    if request.method == "POST":
        subcategory.name = request.POST['name']
        category_id = request.POST['category']
        if "image" in request.FILES:
            subcategory.image = request.FILES["image"]
        subcategory.category = get_object_or_404(Category, pk=category_id)
        subcategory.save()

        return redirect('dashboard:subcategory_list')

    return render(request, 'dashboard/subcategory_edit.html', {
        'subcategory': subcategory,
        'categories': categories
    })

@dashboard_login_required
def subcategory_delete(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)
    subcategory.delete()
    return redirect('dashboard:subcategory_list')


@dashboard_login_required
def inventory(request):
    items = OrderItem.objects.all()  # tumhare DB structure ke hisab se change
    return render(request, 'dashboard/inventory_list.html', {'items': items})



@dashboard_login_required
def dashboard_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password1")
        confirm = request.POST.get("password2")

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect('dashboard:dashboard_register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_staff = True   # MAKE ADMIN
        user.save()

        messages.success(request, "Admin created successfully!")
        return redirect('dashboard:dashboard_login')

    return render(request, "dashboard/register.html")

from contact.models import ContactThread


@dashboard_login_required
def close_thread(request, thread_id):
    thread = get_object_or_404(ContactThread, id=thread_id)
    thread.status = "closed"
    thread.save()

    return redirect(
        "dashboard:dashboard_support_detail",
        thread_id=thread_id
    )
    

@dashboard_login_required
def delete_support_ticket(request, thread_id):

    # 🔒 Custom dashboard auth check
    if not request.session.get("dashboard_user_id"):
        return redirect("dashboard:dashboard_login")

    print("🔥 DELETE VIEW HIT 🔥")
    print("METHOD:", request.method)

    if request.method == "POST":
        thread = get_object_or_404(ContactThread, id=thread_id)
        thread.delete()
        print("🔥 THREAD DELETED 🔥")

    return redirect("/dashboard/support/")


@dashboard_login_required
def slider_list(request):
    sliders = HomeSlider.objects.all()
    return render(request, 'dashboard/slider_list.html', {'sliders': sliders})

# dashboard/views.py

@dashboard_login_required
def slider_add(request):
    if request.method == "POST":
        image = request.FILES.get("image")
        redirect_url = request.POST.get("redirect_url", "").strip()
        is_active = True if request.POST.get("is_active") == "on" else False

        # 🔥 SAFETY: auto add https:// if missing
        if redirect_url and not redirect_url.startswith(("http://", "https://")):
            redirect_url = "https://" + redirect_url

        HomeSlider.objects.create(
            image=image,
            redirect_url=redirect_url,
            is_active=is_active
        )

        return redirect("dashboard:slider_list")

    return render(request, "dashboard/slider_form.html")


@dashboard_login_required
def slider_edit(request, id):
    slider = HomeSlider.objects.get(id=id)

    if request.method == "POST":
        form = HomeSliderForm(request.POST, request.FILES, instance=slider)
        if form.is_valid():
            form.save()
            return redirect('dashboard:slider_list')
    else:
        form = HomeSliderForm(instance=slider)  # 🔥 ye hi main line

    return render(request, "dashboard/slider_form.html", {
        "form": form,
        "slider": slider
    })
    
    
def deals_list(request):
    deals = Deal.objects.select_related("product")

    return render(request, "dashboard/deals_list.html", {
        "deals": deals,
        "now": timezone.now()
    })
    
    
def slider_delete(request, id):
    if request.method == "POST":
        HomeSlider.objects.filter(id=id).delete()

    return redirect('dashboard:slider_list')


def remove_deal(request, id):
    product = Product.objects.get(id=id)
    product.is_deal = False
    product.deal_expiry = None
    product.save()
    return redirect("dashboard:deals_list")

def edit_deal(request, id):
    deal = get_object_or_404(Deal, id=id)

    if request.method == "POST":
        expiry_raw = request.POST.get("expiry")
        discount = request.POST.get("discount_percent")

        if expiry_raw:
            deal.expiry = timezone.make_aware(
                datetime.strptime(expiry_raw, "%Y-%m-%dT%H:%M")
            )

        if discount:
            deal.discount_percent = int(discount)
        else:
            deal.discount_percent = None   # no deal

        deal.save()
        return redirect("dashboard:deals_list")

    return render(request, "dashboard/edit_deal.html", {
        "deal": deal
    })  
    
    
def add_deal(request):
    if request.method == "POST":
        product_id = request.POST.get("product")
        discount_raw = request.POST.get("discount_percent")
        expiry_raw = request.POST.get("expiry")

        # ✅ Convert to Decimal (not int)
        discount = Decimal(discount_raw) if discount_raw else None

        Deal.objects.create(
            product=get_object_or_404(Product, id=product_id),
            discount_percent=discount,
            expiry=timezone.make_aware(
                datetime.strptime(expiry_raw, "%Y-%m-%dT%H:%M")
            )
        )

        return redirect("dashboard:deals_list")

    return render(request, "dashboard/add_deal.html", {
        "categories": Category.objects.all()
    })

    
def delete_deal(request, id):
    deal = get_object_or_404(Deal, id=id)
    deal.delete()
    return redirect("dashboard:deals_list")