from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def cart_detail(request):
    cart = getattr(request.user, "cart", None)
    return render(request, "cart/cart_detail.html", {"cart": cart})
