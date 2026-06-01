from django.contrib import admin

from .models import Payment, PaymentProof


class PaymentProofInline(admin.TabularInline):
    model = PaymentProof
    extra = 0


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "order", "user", "amount", "method", "status", "created_at")
    list_filter = ("status", "method")
    inlines = [PaymentProofInline]


@admin.register(PaymentProof)
class PaymentProofAdmin(admin.ModelAdmin):
    list_display = ("payment", "file", "created_at")
