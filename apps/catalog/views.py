from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def product_list(request):
    selected_category = request.GET.get("category", "")
    sort = request.GET.get("sort", "default")

    products = Product.objects.select_related("category").prefetch_related("images").filter(is_active=True)

    if selected_category:
        products = products.filter(category__slug=selected_category)

    if sort == "price_low":
        products = products.order_by("price")
    elif sort == "price_high":
        products = products.order_by("-price")
    elif sort == "newest":
        products = products.order_by("-created_at")

    categories = Category.objects.filter(is_active=True).annotate(product_count=Count("products")).order_by("name")

    return render(
        request,
        "catalog/product_list.html",
        {
            "products": products,
            "categories": categories,
            "selected_category": selected_category,
            "sort": sort,
            "total_products": products.count(),
        },
    )


def home(request):
    # simple homepage: show featured products and categories
    featured = (
        Product.objects.select_related("category").prefetch_related("images").filter(is_active=True, featured=True)[:6]
    )
    categories = Category.objects.filter(is_active=True).annotate(product_count=Count("products")).order_by("name")
    return render(request, "home.html", {"featured": featured, "categories": categories})


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related("images"),
        slug=slug,
        is_active=True,
    )
    related_products = (
        Product.objects.select_related("category")
        .prefetch_related("images")
        .filter(category=product.category, is_active=True)
        .exclude(pk=product.pk)
        .order_by("-created_at")[:4]
    )
    gallery_images = list(product.images.all())

    return render(
        request,
        "catalog/product_detail.html",
        {
            "product": product,
            "related_products": related_products,
            "gallery_images": gallery_images,
        },
    )
