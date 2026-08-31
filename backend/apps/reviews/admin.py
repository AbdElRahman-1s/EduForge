from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "course", "rating", "created_at")
    list_filter = ("rating", "course")
    search_fields = ("student__username", "course__title")
    ordering = ("-created_at",)
