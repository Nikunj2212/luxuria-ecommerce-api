# ===============================
# DJANGO CORE
# ===============================
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    get_user_model,
    update_session_auth_hash
)
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from products.models import Product
from django.core.mail import send_mail
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from .models import Address
from carts.models import Order
from contact.models import ContactThread, ContactMessage
from .forms import LoginForm, ProfileForm, AddressForm
import json
import random
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from wishlist.models import Wishlist
from decimal import Decimal
from num2words import num2words

User = get_user_model()


def login_view(request):
    if request.method == "POST":
        identifier = request.POST.get("email_or_phone", "").strip()
        password = request.POST.get("password", "").strip()

        user = None

        # ---------- LOGIN VIA EMAIL ----------
        if "@" in identifier:
            try:
                user_obj = User.objects.get(email=identifier)
                user = authenticate(
                    request,
                    username=user_obj.email,  # USERNAME_FIELD = email
                    password=password
                )
            except User.DoesNotExist:
                pass

        # ---------- LOGIN VIA PHONE ----------
        else:
            try:
                user_obj = User.objects.get(phone=identifier)
                user = authenticate(
                    request,
                    username=user_obj.email,  # IMPORTANT
                    password=password
                )
            except User.DoesNotExist:
                pass

        # ---------- SUCCESS ----------
        if user:
            login(request, user)

            # 🔥 FIRST LOGIN CHECK
            if not user.profile_completed:
                return redirect("accounts:complete_profile")

            return redirect("home")

        messages.error(request, "Invalid email/phone or password")

    return render(request, "accounts/login.html")



def signup_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "").strip()

        context = {
            "email": email,
            "phone": phone,
        }

        # Required fields check
        if not email or not password or not phone:
            messages.error(request, "Email, phone and password are required.")
            return render(request, "accounts/signup.html", context)

        # Minimum password length
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, "accounts/signup.html", context)

        # Email duplicate
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "accounts/signup.html", context)

        # Phone duplicate
        if User.objects.filter(phone=phone).exists():
            messages.error(request, "Phone already registered.")
            return render(request, "accounts/signup.html", context)

        # Create user
        user = User.objects.create_user(
            email=email,
            phone=phone,
            password=password
        )

        send_mail(
            "Account Created Successfully 🎉",
            "Your Luxuria account has been created successfully.",
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )

        messages.success(request, "Account created successfully. Please login.")
        return redirect("accounts:login")

    return render(request, "accounts/signup.html")
# =====================================================
# COMPLETE PROFILE
# =====================================================
@login_required
def complete_profile(request):
    address, created = Address.objects.get_or_create(
        user=request.user,
        defaults={
            "house_no": "",
            "address_line1": "",
            "landmark": "",
            "area": "",
            "city": "",
            "state": "",
            "pincode": "",
        }
    )

    if request.method == "POST":
        # ✅ USERNAME
        username = request.POST.get("username", "").strip()

        if not username:
            messages.error(request, "Username is required")
            return render(request, "accounts/complete_profile.html", {
                "address": address
            })

        # 🔒 unique username check
        if User.objects.exclude(id=request.user.id).filter(username=username).exists():
            messages.error(request, "Username already taken")
            return render(request, "accounts/complete_profile.html", {
                "address": address
            })

        request.user.username = username
        request.user.save()

        # ✅ ADDRESS
        address.house_no = request.POST.get("house_no")
        address.address_line1 = request.POST.get("address_line1")
        address.landmark = request.POST.get("landmark")
        address.area = request.POST.get("area")
        address.city = request.POST.get("city")
        address.state = request.POST.get("state")
        address.pincode = request.POST.get("pincode")
        address.save()

        request.user.profile_completed = True
        request.user.save()

        return redirect("home")

    return render(request, "accounts/complete_profile.html", {
        "address": address
    })


# =====================================================
# PROFILE
# =====================================================
@login_required
def profile(request):
    address = Address.objects.filter(user=request.user).first()
    return render(request, "accounts/profile.html", {
        "user": request.user,
        "address": address
    })


# =====================================================
# EDIT ADDRESS
# =====================================================
@login_required
def edit_address(request):
    address, created = Address.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # 🔹 SAVE USERNAME
        username = request.POST.get("username", "").strip()
        if username:
            request.user.username = username
            request.user.save()

        # 🔹 SAVE ADDRESS
        address.house_no = request.POST.get("house_no")
        address.address_line1 = request.POST.get("address_line1")
        address.landmark = request.POST.get("landmark")
        address.area = request.POST.get("area")
        address.city = request.POST.get("city")
        address.state = request.POST.get("state")
        address.pincode = request.POST.get("pincode")
        address.save()

        messages.success(request, "Profile updated successfully")
        return redirect("accounts:profile")

    return render(request, "accounts/edit_address.html", {
        "address": address
    })



# =====================================================
# LOGOUT
# =====================================================
@login_required
def user_logout(request):
    logout(request)
    return redirect("/")


# =====================================================
# HELP CENTER
# =====================================================
@login_required
def help_center(request):
    threads = ContactThread.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "accounts/help_center.html",
        {"threads": threads}
    )


# =====================================================
# TICKET DETAIL
# =====================================================
@login_required
def ticket_detail(request, thread_id):
    thread = get_object_or_404(
        ContactThread,
        id=thread_id,
        user=request.user
    )

    messages_qs = thread.messages.all().order_by("created_at")

    if request.method == "POST":
        text = request.POST.get("message", "").strip()

        if thread.status == "closed":
            messages.error(request, "This ticket is closed")
            return redirect("accounts:ticket_detail", thread_id=thread.id)

        if text:
            ContactMessage.objects.create(
                thread=thread,
                sender="user",
                message=text
            )

        return redirect("accounts:ticket_detail", thread_id=thread.id)

    return render(request, "accounts/ticket_detail.html", {
        "thread": thread,
        "messages": messages_qs
    })


# =====================================================
# ORDERS
# =====================================================
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    products = Product.objects.all()
    return render(request, "accounts/my_orders.html", {
        "orders": orders,
        "products": products
    })

@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, "accounts/track_order.html", {"order": order})


# =====================================================
# DOWNLOAD INVOICE
# =====================================================
@login_required
def download_invoice(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Invoice-{order.order_id}.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=20
    )

    elements = []
    styles = getSampleStyleSheet()

    small = ParagraphStyle(
        'small',
        parent=styles['Normal'],
        fontSize=8,
        leading=10
    )

    # ===== HEADER =====
    elements.append(Paragraph("<b>LUXURIA</b>", styles["Heading1"]))
    elements.append(Paragraph("Tax Invoice / Bill of Supply / Cash Memo", small))
    elements.append(Spacer(1, 10))

    # ===== TOP LEFT / RIGHT =====
    left = f"""
    <b>Sold By:</b><br/>
    Luxuria India Pvt Ltd<br/>
    Ahmedabad, Gujarat<br/>
    GSTIN: 24ABCDE1234F1Z5<br/>
    PAN: ABCDE1234F
    """

    right = f"""
    <b>Billing Address:</b><br/>
    {order.customer_name}<br/>
    {order.address}<br/>
    {order.city} - {order.pincode}<br/>
    {order.customer_email}
    """

    top_table = Table(
        [[Paragraph(left, small), Paragraph(right, small)]],
        colWidths=[3*inch, 3*inch]
    )
    elements.append(top_table)
    elements.append(Spacer(1, 8))

    # ===== META =====
    meta_left = f"""
    <b>Order Number:</b> {order.order_id}<br/>
    <b>Order Date:</b> {order.created_at.strftime('%d.%m.%Y')}
    """

    meta_right = f"""
    <b>Invoice Date:</b> {order.created_at.strftime('%d.%m.%Y')}<br/>
    <b>Payment Mode:</b> {order.payment_method}<br/>
    <b>Status:</b> {order.get_status_display()}
    """

    meta_table = Table(
        [[Paragraph(meta_left, small), Paragraph(meta_right, small)]],
        colWidths=[3*inch, 3*inch]
    )
    elements.append(meta_table)
    elements.append(Spacer(1, 12))

    # ===== PRODUCT TABLE =====
    data = [["Sl", "Description", "Unit Price", "Qty", "Amount"]]

    total = Decimal("0.00")
    count = 1

    for item in order.items.all():
        subtotal = item.price * item.quantity
        total += subtotal

        data.append([
            str(count),
            Paragraph(item.product_name, small),
            f"{item.price:.2f}",
            str(item.quantity),
            f"{subtotal:.2f}"
        ])
        count += 1

    data.append(["", "", "", "Total", f"{order.total_amount:.2f}"])

    table = Table(
        data,
        colWidths=[0.5*inch, 3.2*inch, 0.9*inch, 0.6*inch, 1*inch]
    )

    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.4, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN', (2,1), (-1,-2), 'RIGHT'),
        ('ALIGN', (3,1), (3,-2), 'CENTER'),
        ('ALIGN', (4,1), (-1,-1), 'RIGHT'),
        ('SPAN', (0,-1), (3,-1)),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 8))

    # ===== AMOUNT WORDS =====
    elements.append(Paragraph("<b>Amount in Words:</b>", small))
    amount_words = num2words(order.total_amount, lang='en_IN').title()
    elements.append(Paragraph(f"{amount_words} Rupees Only", small))
    elements.append(Spacer(1, 25))

    elements.append(Paragraph("For Luxuria India Pvt Ltd", small))
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Authorized Signatory", small))

    doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
    return response

def add_footer(canvas, doc):
    canvas.saveState()
    
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    
    footer_text = "This is a computer generated invoice. No signature required."
    
    width, height = A4
    canvas.drawCentredString(width / 2.0, 0.5 * inch, footer_text)
    
    canvas.restoreState()
# =====================================================
# CHANGE PASSWORD
# =====================================================
@login_required
def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        user = request.user

        # 🔴 1. Check old password
        if not user.check_password(old_password):
            messages.error(request, "Current password is incorrect.")
            return redirect("accounts:change_password")

        # 🔴 2. Check new passwords match
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect("accounts:change_password")

        # 🔴 3. Optional: Minimum length check
        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect("accounts:change_password")

        # ✅ All good — change password
        user.set_password(new_password)
        user.save()

        # 🔥 IMPORTANT: Keep user logged in
        update_session_auth_hash(request, user)

        messages.success(request, "Password updated successfully.")
        return redirect("accounts:change_password")

    return render(request, "accounts/change_password.html")

# =====================================================
# FORGOT PASSWORD PAGE
# =====================================================
def forgot_password(request):
    return render(request, "accounts/forgot_password.html")


# =====================================================
# OTP SEND
# =====================================================
@csrf_exempt
def send_otp(request):
    data = json.loads(request.body)
    email = data.get("email", "").strip()

    try:
        User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Email not registered"})

    otp = str(random.randint(100000, 999999))
    request.session["fp_otp"] = otp
    request.session["fp_email"] = email

    send_mail(
        "Your OTP Code",
        f"Your OTP is {otp}",
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )

    return JsonResponse({"status": "ok", "message": "OTP sent"})


# =====================================================
# OTP VERIFY
# =====================================================
@csrf_exempt
def verify_otp(request):
    data = json.loads(request.body)

    if data.get("otp") == request.session.get("fp_otp"):
        request.session["fp_verified"] = True
        return JsonResponse({"status": "ok", "message": "OTP verified"})

    return JsonResponse({"status": "error", "message": "Invalid OTP"})


# =====================================================
# RESET PASSWORD
# =====================================================
@csrf_exempt
def reset_password(request):
    data = json.loads(request.body)

    if not request.session.get("fp_verified"):
        return JsonResponse({"status": "error", "message": "OTP not verified"})

    if data["password1"] != data["password2"]:
        return JsonResponse({"status": "error", "message": "Passwords do not match"})

    user = User.objects.get(email=request.session["fp_email"])
    user.set_password(data["password1"])
    user.save()

    request.session.flush()
    return JsonResponse({"status": "ok", "message": "Password reset successful"})


@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    wishlist_products = [item.product for item in wishlist_items]

    return render(request, "accounts/wishlist.html", {
        "wishlist_products": wishlist_products
    })