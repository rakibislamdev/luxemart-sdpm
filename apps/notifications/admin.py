from django.contrib import admin

from .models import ContactSubmission, Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "is_read", "created_at")
    list_filter = ("is_read",)
    search_fields = ("title", "message")


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "is_reviewed", "created_at")
    list_filter = ("is_reviewed", "created_at")
    search_fields = ("name", "email", "message")
    readonly_fields = ("created_at", "updated_at")
