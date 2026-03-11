from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from products.models import Product
from .models import Order, OrderItem, Coupon
from accounts.models import Address
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from .models import Cart
from products.models import Product 
from num2words import num2words
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum
from django.shortcuts import get_object_or_404


# =====================================================
# CART (SESSION BASED)
# =====================================================
@login_required(login_url='login')
def add_to_cart(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    qty = int(request.GET.get("qty", 1))

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += qty
    else:
        cart_item.quantity = qty

    cart_item.save()

    cart_count = Cart.objects.filter(user=request.user).aggregate(
        total=Sum("quantity")
    )["total"] or 0

    # 👇 KEY FIX
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"cart_count": cart_count})

    return redirect("carts:cart")

@login_required(login_url='login')
def cart_detail(request):

    cart_items = Cart.objects.filter(user=request.user)
    total = 0

    for item in cart_items:
        item.subtotal = item.product.price * item.quantity
        total += item.subtotal

    return render(request, "carts/cart_detail.html", {
        "cart_items": cart_items,
        "total": total
    })


@login_required(login_url='login')
def increase_qty(request, id):

    cart_item = get_object_or_404(Cart, id=id, user=request.user)
    cart_item.quantity += 1
    cart_item.save()

    return redirect('carts:cart')



@login_required(login_url='login')
def decrease_qty(request, id):

    cart_item = get_object_or_404(Cart, id=id, user=request.user)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('carts:cart')



@login_required(login_url='login')
def remove_from_cart(request, id):
    cart_item = get_object_or_404(Cart, id=id, user=request.user)
    cart_item.delete()
    return redirect("carts:cart")

# =====================================================
# CHECKOUT = SHIPPING + ADDRESS EDIT + NEXT
# =====================================================

@login_required(login_url='login')
def checkout(request):

    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect("carts:cart")

    total = 0
    for item in cart_items:
        total += item.product.price * item.quantity

    address, created = Address.objects.get_or_create(user=request.user)

    if request.method == "POST" and "phone" in request.POST:
        address.phone = request.POST.get("phone")
        address.house_no = request.POST.get("house_no")
        address.address_line1 = request.POST.get("address_line1")
        address.landmark = request.POST.get("landmark")
        address.area = request.POST.get("area")
        address.city = request.POST.get("city")
        address.state = request.POST.get("state")
        address.pincode = request.POST.get("pincode")
        address.save()
        return redirect("carts:checkout")

    return render(request, "carts/checkout.html", {
        "address": address,
        "total": total
    })


# =====================================================
# PAYMENT (ORDER CREATE HERE — ONLY ONCE)
# =====================================================
@login_required(login_url='login')
def payment_method(request):

    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect("carts:cart")

    total = 0
    for item in cart_items:
        total += item.product.price * item.quantity

    if request.method == "POST":
        method = request.POST.get("method")
        request.session["payment_method"] = method
        return redirect("carts:payment_gateway")

    return render(request, "carts/payment_method.html", {
        "total": total
    })

    
@login_required(login_url='login')
def payment_gateway(request):

    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect("carts:cart")

    method = request.session.get("payment_method")

    if not method:
        return redirect("carts:payment_method")

    total = 0
    for item in cart_items:
        total += item.product.price * item.quantity

    if request.method == "POST":
        return redirect("carts:processing")

    return render(request, "carts/fake_gateway.html", {
        "total": total,
        "method": method
    })




@login_required(login_url='login')
def buy_now(request, product_id):

    product = get_object_or_404(Product, id=product_id)
    qty = int(request.GET.get("qty", 1))

    # Purana cart clear nahi kar rahe (optional)
    # Agar sirf ye product hi checkout karwana hai to cart clear kar sakte hai:
    Cart.objects.filter(user=request.user).delete()

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    cart_item.quantity = qty
    cart_item.save()

    return redirect("carts:checkout")


@login_required(login_url='login')
def process_payment(request):

    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect("carts:cart")

    address = get_object_or_404(Address, user=request.user)

    total = Decimal("0.00")

    for item in cart_items:
        total += item.product.price * item.quantity

    coupon_code = request.session.get("coupon")
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            discount_amount = (total * coupon.discount) / 100
            total -= discount_amount
        except:
            pass

    payment_method = request.session.get("payment_method", "COD")

    order = Order.objects.create(
        order_id=str(uuid.uuid4()),
        user=request.user,
        customer_name=request.user.username,
        customer_email=request.user.email,
        phone=request.user.phone,
        address=f"{address.house_no}, {address.address_line1}, {address.landmark}, {address.area}",
        city=address.city,
        pincode=address.pincode,
        payment_method=payment_method,
        status="PAID",
        total_amount=total
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product_name=item.product.name,
            quantity=item.quantity,
            price=item.product.price
        )

    # EMAIL
    send_order_email(order)

    # 🔥 IMPORTANT — CLEAR DB CART
    cart_items.delete()

    # CLEAR SESSION
    request.session.pop("coupon", None)
    request.session.pop("payment_method", None)

    return redirect("carts:payment_success", order_id=order.order_id)


@login_required(login_url='login')
def processing(request):
    order_id = request.session.get("last_order")
    if not order_id:
        return redirect("carts:cart")

    return render(request, "carts/processing.html", {"order_id": order_id})


@login_required(login_url='login')
def payment_success(request, order_id):

    order = get_object_or_404(Order, order_id=order_id)

    Cart.objects.filter(user=request.user).delete()

    return render(request, "carts/success.html", {
        "order": order
    })



# =====================================================
# PDF INVOICE
# =====================================================

@login_required
def invoice_view(request, order_id):
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
    width, height = A4

    canvas.setStrokeColor(colors.grey)
    canvas.setLineWidth(0.5)

    # Line
    canvas.line(25, 40, width - 25, 40)

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)

    footer_text = "This is a computer-generated invoice and does not require a signature."

    canvas.drawCentredString(width / 2, 28, footer_text)

    page_number_text = f"Page {doc.page}"
    canvas.drawRightString(width - 30, 28, page_number_text)


def send_order_email(order):
    subject = f"Luxuria Order Confirmation - {order.order_id}"
    message = f"""
Hi {order.customer_name},

Thank you for shopping with Luxuria 🛍️

Order ID: {order.order_id}
Amount Paid: ₹{order.total_amount}
Payment Method: {order.payment_method}

Your order is confirmed and being prepared.

Team Luxuria
"""
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [order.customer_email],
        fail_silently=True,
    )



@login_required(login_url='login')
def clear_cart(request):
    Cart.objects.filter(user=request.user).delete()
    return redirect("carts:cart")

