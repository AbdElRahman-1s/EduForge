from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "course", "amount", "status", "created_at")
    list_filter = ("status", "course")
    search_fields = ("student__username", "course__title")
    ordering = ("-created_at",)
