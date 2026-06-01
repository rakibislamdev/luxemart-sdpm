from django.contrib import admin

from .models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock_quantity", "is_active", "featured")
    list_filter = ("is_active", "featured", "category")
    search_fields = ("name", "sku")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "is_primary", "created_at")
