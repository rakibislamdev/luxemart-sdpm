from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def order_history(request):
    return render(request, "orders/order_history.html")
