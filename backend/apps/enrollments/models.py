from django.db import models
from django.contrib.auth import get_user_model
from apps.courses.models import Course

user = get_user_model()


# Create your models here.
class Enrollment(models.Model):
    student = models.ForeignKey(
        user, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrollments"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course")
        ordering = ["-enrolled_at"]

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"
