from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class Notification(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.title
