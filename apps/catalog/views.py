from django.shortcuts import get_object_or_404, render

from .models import Product


def product_list(request):
    products = Product.objects.select_related("category").prefetch_related("images").filter(is_active=True)
    return render(request, "catalog/product_list.html", {"products": products})


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category").prefetch_related("images"), slug=slug, is_active=True)
    return render(request, "catalog/product_detail.html", {"product": product})
