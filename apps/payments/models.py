from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel
from apps.orders.models import Order


class Payment(TimeStampedModel):
    class Method(models.TextChoices):
        BKASH = "bkash", "bKash"
        NAGAD = "nagad", "Nagad"
        ROCKET = "rocket", "Rocket"
        CARD = "card", "Debit/Credit Card"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=Method.choices)
    transaction_id = models.CharField(max_length=120, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    def __str__(self):
        return f"Payment {self.transaction_id}"


class PaymentProof(TimeStampedModel):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="proofs")
    file = models.FileField(upload_to="payment-proofs/")
    description = models.CharField(max_length=255, blank=True)
