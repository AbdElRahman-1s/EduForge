from rest_framework import serializers
from .models import Enrollment
from apps.courses.serializers import InstructorSerializer


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ["id", "course_id", "enrolled_at"]
        read_only_fields = ["id", "enrolled_at"]


class MyEnrollmentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="course.id", read_only=True)
    title = serializers.CharField(source="course.title", read_only=True)
    thumbnail = serializers.ImageField(source="course.thumbnail", read_only=True)
    badge = serializers.CharField(source="course.badge", read_only=True)
    category = serializers.CharField(source="course.category.name", read_only=True)
    level = serializers.CharField(source="course.level", read_only=True)
    total_lessons = serializers.IntegerField(read_only=True)
    total_duration_seconds = serializers.IntegerField(read_only=True)
    instructor = instructor = InstructorSerializer(
        source="course.instructor", read_only=True
    )
    progress_percent = serializers.IntegerField(default=0)

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "title",
            "thumbnail",
            "badge",
            "category",
            "level",
            "total_lessons",
            "total_duration_seconds",
            "instructor",
            "enrolled_at",
            "progress_percent",
        ]
        read_only_fields = [
            "id",
            "enrolled_at",
            "title",
            "thumbnail",
            "instructor",
            "progress_percent",
        ]
