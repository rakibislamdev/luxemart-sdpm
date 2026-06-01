from django.conf import settings
from django.db import models

from apps.catalog.models import Product
from apps.common.models import TimeStampedModel


class Order(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.pk}"


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)


class DeliveryInformation(TimeStampedModel):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="delivery_information")
    tracking_number = models.CharField(max_length=100, blank=True)
    carrier = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=50, default="pending")
    delivered_at = models.DateTimeField(null=True, blank=True)
