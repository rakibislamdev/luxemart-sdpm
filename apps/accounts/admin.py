from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Role, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (("Profile", {"fields": ("role", "phone_number", "avatar", "is_active_customer")}),)
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active", "is_superuser")
