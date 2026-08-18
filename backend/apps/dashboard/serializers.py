from rest_framework import serializers
from apps.courses.models import Course
from apps.enrollments.models import Enrollment


class DashboardCourseSerializer(serializers.ModelSerializer):
    student_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "thumbnail",
            "published",
            "student_count",
        ]


class DashboardSignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="student.username", read_only=True)
    email = serializers.EmailField(source="student.email", read_only=True)
    enrollment_id = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "enrollment_id",
            "username",
            "email",
            "status",
        ]


class DashboardOverviewSerializer(serializers.Serializer):
    total_courses = serializers.IntegerField()
    total_students = serializers.IntegerField()
    recent_courses = DashboardCourseSerializer(many=True, read_only=True)
    recent_signups = DashboardSignupSerializer(many=True, read_only=True)
