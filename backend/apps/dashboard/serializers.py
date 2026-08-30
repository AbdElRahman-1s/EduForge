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

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "username",
            "email",
            "status",
        ]


class DashboardOverviewSerializer(serializers.Serializer):
    total_courses = serializers.IntegerField()
    total_students = serializers.IntegerField()
    recent_courses = DashboardCourseSerializer(many=True, read_only=True)
    recent_signups = DashboardSignupSerializer(many=True, read_only=True)


class InstructorCourseSerializer(serializers.ModelSerializer):
    category = serializers.ReadOnlyField(source="category.name")
    enrollment_count = serializers.IntegerField(read_only=True)
    review_count = serializers.IntegerField(read_only=True, default=0)
    avg_rating = serializers.FloatField(read_only=True, default=0.0)
    lesson_count = serializers.IntegerField(read_only=True)
    total_duration = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "thumbnail",
            "category",
            "enrollment_count",
            "review_count",
            "avg_rating",
            "lesson_count",
            "total_duration",
            "price",
        ]


class InstructorStudentSerializer(serializers.Serializer):
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    course_count = serializers.IntegerField(read_only=True)
    joined_at = serializers.DateTimeField(format="%Y:%m:%d", read_only=True)
