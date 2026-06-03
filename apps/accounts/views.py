from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import UserRegistrationForm


@login_required
def profile(request):
    return render(request, "accounts/profile.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("catalog:product-list")
    
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='apps.accounts.backends.EmailOrUsernameBackend')
            messages.success(request, f"Welcome {user.first_name}! Your account has been created successfully.")
            return redirect("home")
    else:
        form = UserRegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("catalog:product-list")
