from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from apps.cart.models import Cart
from apps.payments.models import Payment

from .models import Order, OrderItem


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "orders/order_history.html", {"orders": orders})


@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    if not cart.items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect("catalog:product-list")

    if request.method == "POST":
        # Simplified checkout: create order from cart
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                total_amount=cart.total_amount,
                status=Order.Status.PENDING
            )
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.product.price
                )
            
            # Clear cart
            cart.items.all().delete()
            
            # Create a pending payment record
            Payment.objects.create(
                order=order,
                user=request.user,
                amount=order.total_amount,
                method=Payment.Method.CARD, # Default for mock
                transaction_id=f"TXN-{order.id}-{request.user.id}",
                status=Payment.Status.PENDING
            )

        messages.success(request, "Order placed successfully!")
        return redirect("orders:success", order_id=order.id)

    return render(request, "orders/checkout.html", {"cart": cart})


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "orders/order_success.html", {"order": order})
