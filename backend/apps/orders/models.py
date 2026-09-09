from django.conf import settings
from django.db import models

from apps.courses.models import Course


class Order(models.Model):
    """A single purchase attempt — a price snapshot, not ownership."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"
        EXPIRED = "expired", "Expired"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="orders"
    )
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    provider_reference = models.CharField(
        max_length=255, blank=True, default=""
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.username} order #{self.pk} for {self.course.title}"
