from django.contrib import admin
from .models import Course, Category, Topic, Section, Lesson

# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "instructor",
        "category",
        "level",
        "price",
        "published",
    )
    list_filter = ("published", "category", "level")
    search_fields = ("title", "instructor__username")
    ordering = ("-created_at",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "course", "order")
    list_filter = ("course",)
    search_fields = ("title",)
    ordering = ("course", "order")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "section",
        "order",
        "duration_seconds",
        "free",
    )
    list_filter = ("free", "section__course")
    search_fields = ("title",)
    ordering = ("section", "order")
