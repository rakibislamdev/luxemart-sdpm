from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def payment_list(request):
    return render(request, "payments/payment_list.html")
