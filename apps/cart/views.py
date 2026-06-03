from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.catalog.models import Product

from .models import Cart, CartItem


@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, "cart/cart_detail.html", {"cart": cart})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart, created = Cart.objects.get_or_create(user=request.user)
    quantity = int(request.POST.get("quantity", 1))

    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not item_created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()

    messages.success(request, f"Added {product.name} to your cart.")
    return redirect("cart:detail")


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f"Removed {product_name} from your cart.")
    return redirect("cart:detail")
