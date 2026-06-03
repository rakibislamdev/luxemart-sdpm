from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q, Sum
from django.db.models.deletion import ProtectedError
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.models import Role
from apps.catalog.models import Category, Product, ProductImage
from apps.orders.models import DeliveryInformation, Order, OrderItem
from apps.payments.models import Payment

from .forms import (
    CategoryForm,
    DeliveryInformationForm,
    OrderStatusForm,
    PaymentStatusForm,
    ProductForm,
    RoleForm,
    UserManagementForm,
)


MONEY_ZERO = Decimal("0.00")


def money_sum(queryset, field):
    return queryset.aggregate(total=Sum(field)).get("total") or MONEY_ZERO


def status_breakdown(queryset, field, choices):
    total = queryset.count()
    counts = dict(queryset.values_list(field).annotate(count=Count("id")))
    return [
        {
            "value": value,
            "label": label,
            "count": counts.get(value, 0),
            "percent": round((counts.get(value, 0) / total) * 100) if total else 0,
        }
        for value, label in choices
    ]


def admin_context(active):
    return {
        "active_admin_section": active,
        "admin_nav": [
            {"label": "Dashboard", "url_name": "management:home", "key": "home"},
            {"label": "Products", "url_name": "management:products", "key": "products"},
            {"label": "Categories", "url_name": "management:categories", "key": "categories"},
            {"label": "Orders", "url_name": "management:orders", "key": "orders"},
            {"label": "Payments", "url_name": "management:payments", "key": "payments"},
            {"label": "Deliveries", "url_name": "management:deliveries", "key": "deliveries"},
            {"label": "Users & Roles", "url_name": "management:users", "key": "users"},
            {"label": "Reports", "url_name": "management:reports", "key": "reports"},
            {"label": "Django Admin", "url_name": "admin:index", "key": "django-admin"},
        ],
    }


@staff_member_required
def home(request):
    approved_payments = Payment.objects.filter(status=Payment.Status.APPROVED)
    delivered_orders = Order.objects.filter(status=Order.Status.DELIVERED)
    line_total = ExpressionWrapper(
        F("quantity") * F("unit_price"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )

    monthly_sales = list(
        approved_payments.annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Sum("amount"), payments=Count("id"))
        .order_by("-month")[:6]
    )

    top_products = (
        OrderItem.objects.values("product__name", "product__sku")
        .annotate(units=Sum("quantity"), sales=Sum(line_total))
        .order_by("-sales")[:6]
    )

    context = {
        **admin_context("home"),
        "total_users": get_user_model().objects.count(),
        "active_customers": get_user_model().objects.filter(is_active=True, is_active_customer=True).count(),
        "total_products": Product.objects.count(),
        "active_products": Product.objects.filter(is_active=True).count(),
        "low_stock_count": Product.objects.filter(stock_quantity__lte=5).count(),
        "total_categories": Category.objects.count(),
        "total_orders": Order.objects.count(),
        "pending_orders": Order.objects.filter(status=Order.Status.PENDING).count(),
        "pending_payments": Payment.objects.filter(status=Payment.Status.PENDING).count(),
        "total_revenue": money_sum(approved_payments, "amount"),
        "total_sales": money_sum(delivered_orders, "total_amount"),
        "order_statuses": status_breakdown(Order.objects.all(), "status", Order.Status.choices),
        "payment_statuses": status_breakdown(Payment.objects.all(), "status", Payment.Status.choices),
        "monthly_sales": monthly_sales,
        "top_products": top_products,
        "low_stock_products": Product.objects.select_related("category").order_by("stock_quantity", "name")[:8],
        "recent_orders": Order.objects.select_related("user").order_by("-created_at")[:8],
        "recent_payments": Payment.objects.select_related("user", "order").order_by("-created_at")[:8],
    }
    return render(request, "dashboard/home.html", context)


@staff_member_required
def categories(request):
    edit_category = None
    form = CategoryForm()

    if request.GET.get("edit"):
        edit_category = get_object_or_404(Category, pk=request.GET["edit"])
        form = CategoryForm(instance=edit_category)

    if request.method == "POST":
        action = request.POST.get("action")
        category = None
        if request.POST.get("category_id"):
            category = get_object_or_404(Category, pk=request.POST["category_id"])

        if action == "save":
            form = CategoryForm(request.POST, instance=category)
            if form.is_valid():
                form.save()
                messages.success(request, "Category saved.")
                return redirect("management:categories")
            edit_category = category
        elif action == "toggle" and category:
            category.is_active = not category.is_active
            category.save(update_fields=["is_active", "updated_at"])
            messages.success(request, "Category status updated.")
            return redirect("management:categories")
        elif action == "delete" and category:
            try:
                category.delete()
                messages.success(request, "Category deleted.")
            except ProtectedError:
                messages.error(request, "This category has products, so deactivate it instead of deleting it.")
            return redirect("management:categories")

    category_list = Category.objects.annotate(product_count=Count("products")).order_by("name")
    return render(
        request,
        "dashboard/categories.html",
        {**admin_context("categories"), "categories": category_list, "form": form, "edit_category": edit_category},
    )


@staff_member_required
def products(request):
    edit_product = None
    form = ProductForm()

    if request.GET.get("edit"):
        edit_product = get_object_or_404(Product.objects.select_related("category"), pk=request.GET["edit"])
        form = ProductForm(instance=edit_product)

    if request.method == "POST":
        action = request.POST.get("action")
        product = None
        if request.POST.get("product_id"):
            product = get_object_or_404(Product, pk=request.POST["product_id"])

        if action == "save":
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                saved_product = form.save(commit=False)
                if not saved_product.pk:
                    saved_product.created_by = request.user
                saved_product.save()
                image = request.FILES.get("image")
                if image:
                    # Make new upload the primary image and unset others
                    saved_product.images.filter(is_primary=True).update(is_primary=False)
                    ProductImage.objects.create(
                        product=saved_product,
                        image=image,
                        alt_text=saved_product.name,
                        is_primary=True,
                    )
                messages.success(request, "Product saved.")
                return redirect("management:products")
            edit_product = product
        elif action == "toggle_active" and product:
            product.is_active = not product.is_active
            product.save(update_fields=["is_active", "updated_at"])
            messages.success(request, "Product availability updated.")
            return redirect("management:products")
        elif action == "toggle_featured" and product:
            product.featured = not product.featured
            product.save(update_fields=["featured", "updated_at"])
            messages.success(request, "Featured status updated.")
            return redirect("management:products")
        elif action == "delete" and product:
            try:
                product.delete()
                messages.success(request, "Product deleted.")
            except ProtectedError:
                messages.error(request, "This product is tied to orders, so deactivate it instead of deleting it.")
            return redirect("management:products")

    search = request.GET.get("q", "").strip()
    stock_filter = request.GET.get("stock", "")
    product_list = Product.objects.select_related("category").prefetch_related("images").order_by("-created_at")
    if search:
        product_list = product_list.filter(Q(name__icontains=search) | Q(sku__icontains=search))
    if stock_filter == "low":
        product_list = product_list.filter(stock_quantity__lte=5)
    elif stock_filter == "out":
        product_list = product_list.filter(stock_quantity=0)
    elif stock_filter == "active":
        product_list = product_list.filter(is_active=True)
    elif stock_filter == "inactive":
        product_list = product_list.filter(is_active=False)

    return render(
        request,
        "dashboard/products.html",
        {
            **admin_context("products"),
            "products": product_list,
            "form": form,
            "edit_product": edit_product,
            "search": search,
            "stock_filter": stock_filter,
        },
    )


@staff_member_required
def users(request):
    User = get_user_model()
    edit_user = None
    edit_role = None
    user_form = None
    role_form = RoleForm()

    if request.GET.get("edit_user"):
        edit_user = get_object_or_404(User, pk=request.GET["edit_user"])
        user_form = UserManagementForm(instance=edit_user)
    if request.GET.get("edit_role"):
        edit_role = get_object_or_404(Role, pk=request.GET["edit_role"])
        role_form = RoleForm(instance=edit_role)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "save_user":
            user = get_object_or_404(User, pk=request.POST["user_id"])
            user_form = UserManagementForm(request.POST, instance=user)
            if user_form.is_valid():
                managed_user = user_form.save(commit=False)
                if managed_user.pk == request.user.pk:
                    managed_user.is_staff = True
                    managed_user.is_active = True
                managed_user.save()
                messages.success(request, "User access updated.")
                return redirect("management:users")
            edit_user = user
        elif action == "toggle_user":
            user = get_object_or_404(User, pk=request.POST["user_id"])
            if user.pk == request.user.pk:
                messages.error(request, "You cannot deactivate your own admin account.")
            else:
                user.is_active = not user.is_active
                user.save(update_fields=["is_active"])
                messages.success(request, "User status updated.")
            return redirect("management:users")
        elif action == "save_role":
            role = Role.objects.filter(pk=request.POST.get("role_id")).first()
            role_form = RoleForm(request.POST, instance=role)
            if role_form.is_valid():
                role_form.save()
                messages.success(request, "Role saved.")
                return redirect("management:users")
            edit_role = role
        elif action == "toggle_role":
            role = get_object_or_404(Role, pk=request.POST["role_id"])
            role.is_active = not role.is_active
            role.save(update_fields=["is_active", "updated_at"])
            messages.success(request, "Role status updated.")
            return redirect("management:users")

    user_list = User.objects.select_related("role").annotate(order_count=Count("orders")).order_by("-date_joined")
    roles = Role.objects.annotate(user_count=Count("user")).order_by("name")
    return render(
        request,
        "dashboard/users.html",
        {
            **admin_context("users"),
            "users": user_list,
            "roles": roles,
            "user_form": user_form,
            "role_form": role_form,
            "edit_user": edit_user,
            "edit_role": edit_role,
        },
    )


@staff_member_required
def orders(request):
    if request.method == "POST":
        order = get_object_or_404(Order, pk=request.POST["order_id"])
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            DeliveryInformation.objects.get_or_create(order=order)
            messages.success(request, f"Order #{order.pk} status updated.")
        else:
            messages.error(request, "Could not update order status.")
        return redirect("management:orders")

    status_filter = request.GET.get("status", "")
    order_list = Order.objects.select_related("user").prefetch_related("items__product").order_by("-created_at")
    if status_filter:
        order_list = order_list.filter(status=status_filter)

    return render(
        request,
        "dashboard/orders.html",
        {
            **admin_context("orders"),
            "orders": order_list,
            "status_filter": status_filter,
            "status_choices": Order.Status.choices,
            "status_breakdown": status_breakdown(Order.objects.all(), "status", Order.Status.choices),
        },
    )


@staff_member_required
def payments(request):
    if request.method == "POST":
        payment = get_object_or_404(Payment, pk=request.POST["payment_id"])
        form = PaymentStatusForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            messages.success(request, f"Payment {payment.transaction_id} updated.")
        else:
            messages.error(request, "Could not update payment.")
        return redirect("management:payments")

    status_filter = request.GET.get("status", "")
    payment_list = Payment.objects.select_related("user", "order").prefetch_related("proofs").order_by("-created_at")
    if status_filter:
        payment_list = payment_list.filter(status=status_filter)

    return render(
        request,
        "dashboard/payments.html",
        {
            **admin_context("payments"),
            "payments": payment_list,
            "status_filter": status_filter,
            "status_choices": Payment.Status.choices,
            "status_breakdown": status_breakdown(Payment.objects.all(), "status", Payment.Status.choices),
            "pending_amount": money_sum(Payment.objects.filter(status=Payment.Status.PENDING), "amount"),
            "approved_amount": money_sum(Payment.objects.filter(status=Payment.Status.APPROVED), "amount"),
        },
    )


@staff_member_required
def deliveries(request):
    if request.method == "POST":
        delivery = get_object_or_404(DeliveryInformation, pk=request.POST["delivery_id"])
        form = DeliveryInformationForm(request.POST, instance=delivery)
        if form.is_valid():
            saved_delivery = form.save(commit=False)
            if saved_delivery.status.lower() == "delivered" and not saved_delivery.delivered_at:
                saved_delivery.delivered_at = timezone.now()
            saved_delivery.save()
            messages.success(request, f"Delivery for order #{delivery.order_id} updated.")
        else:
            messages.error(request, "Could not update delivery.")
        return redirect("management:deliveries")

    missing_delivery_orders = Order.objects.filter(delivery_information__isnull=True).exclude(status=Order.Status.CANCELLED)
    for order in missing_delivery_orders:
        DeliveryInformation.objects.get_or_create(order=order)
    delivery_list = DeliveryInformation.objects.select_related("order", "order__user").order_by("-updated_at")

    return render(
        request,
        "dashboard/deliveries.html",
        {
            **admin_context("deliveries"),
            "deliveries": delivery_list,
            "delivery_statuses": DeliveryInformation.objects.values("status").annotate(count=Count("id")).order_by("status"),
        },
    )


@staff_member_required
def reports(request):
    line_total = ExpressionWrapper(
        F("quantity") * F("unit_price"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )
    approved_payments = Payment.objects.filter(status=Payment.Status.APPROVED)
    monthly_sales = (
        approved_payments.annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Sum("amount"), payments=Count("id"))
        .order_by("-month")[:12]
    )
    category_performance = (
        OrderItem.objects.values("product__category__name")
        .annotate(units=Sum("quantity"), sales=Sum(line_total), products=Count("product", distinct=True))
        .order_by("-sales")
    )
    product_performance = (
        OrderItem.objects.values("product__name", "product__sku", "product__stock_quantity")
        .annotate(units=Sum("quantity"), sales=Sum(line_total))
        .order_by("-sales")[:15]
    )

    return render(
        request,
        "dashboard/reports.html",
        {
            **admin_context("reports"),
            "monthly_sales": monthly_sales,
            "category_performance": category_performance,
            "product_performance": product_performance,
            "total_revenue": money_sum(approved_payments, "amount"),
            "average_order_value": money_sum(Order.objects.all(), "total_amount") / max(Order.objects.count(), 1),
            "conversion_queue": {
                "pending_orders": Order.objects.filter(status=Order.Status.PENDING).count(),
                "pending_payments": Payment.objects.filter(status=Payment.Status.PENDING).count(),
                "low_stock": Product.objects.filter(stock_quantity__lte=5).count(),
            },
        },
    )
