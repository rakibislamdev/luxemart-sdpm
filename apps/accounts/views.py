from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html")


@require_POST
def logout_view(request):
    logout(request)
    return redirect("catalog:product-list")
