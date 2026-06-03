from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def product_list(request):
    selected_category = request.GET.get("category", "")
    search_query = request.GET.get("q", "").strip()
    price_range = request.GET.get("price", "all")
    availability = request.GET.get("availability", "all")
    sort = request.GET.get("sort", "default")

    products = Product.objects.select_related("category").prefetch_related("images").filter(is_active=True)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(sku__icontains=search_query)
            | Q(category__name__icontains=search_query)
        )

    if selected_category:
        products = products.filter(category__slug=selected_category)

    price_ranges = [
        {"value": "all", "label": "All prices", "min": None, "max": None},
        {"value": "under-500", "label": "Under ৳500", "min": None, "max": 500},
        {"value": "500-1000", "label": "৳500 - ৳1,000", "min": 500, "max": 1000},
        {"value": "1000-5000", "label": "৳1,000 - ৳5,000", "min": 1000, "max": 5000},
        {"value": "over-5000", "label": "Over ৳5,000", "min": 5000, "max": None},
    ]
    selected_price_range = next((item for item in price_ranges if item["value"] == price_range), price_ranges[0])
    if selected_price_range["min"] is not None:
        products = products.filter(price__gte=selected_price_range["min"])
    if selected_price_range["max"] is not None:
        products = products.filter(price__lte=selected_price_range["max"])

    if availability == "in_stock":
        products = products.filter(stock_quantity__gt=0)
    elif availability == "low_stock":
        products = products.filter(stock_quantity__gt=0, stock_quantity__lte=5)
    elif availability == "out_of_stock":
        products = products.filter(stock_quantity=0)

    if sort == "price_low":
        products = products.order_by("price")
    elif sort == "price_high":
        products = products.order_by("-price")
    elif sort == "newest":
        products = products.order_by("-created_at")
    elif sort == "stock":
        products = products.order_by("-stock_quantity", "name")
    else:
        products = products.order_by("name")

    categories = (
        Category.objects.filter(is_active=True)
        .annotate(product_count=Count("products", filter=Q(products__is_active=True)))
        .order_by("name")
    )

    return render(
        request,
        "catalog/product_list.html",
        {
            "products": products,
            "categories": categories,
            "selected_category": selected_category,
            "search_query": search_query,
            "price_range": price_range,
            "price_ranges": price_ranges,
            "availability": availability,
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
    gallery_images = list(product.images.all().order_by("-is_primary", "-created_at"))

    return render(
        request,
        "catalog/product_detail.html",
        {
            "product": product,
            "related_products": related_products,
            "gallery_images": gallery_images,
        },
    )
