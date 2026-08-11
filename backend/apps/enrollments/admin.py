from django.contrib import admin
from backend.apps.enrollments.models import Enrollment


# Register your models here.
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "enrolled_at")
    search_fields = ("student__username", "course__title")
    list_filter = ("enrolled_at",)
    ordering = ("-enrolled_at",)


admin.site.register(Enrollment, EnrollmentAdmin)
