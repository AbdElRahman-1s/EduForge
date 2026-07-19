from rest_framework import serializers
from .models import Course
from apps.accounts.models import User


class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
        ]


class CourseCreateSerializer(serializers.ModelSerializer):
    instructor = InstructorSerializer(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "instructor",
            "published",
            "created_at",
        ]
