from django.core.validators import MinLengthValidator, MaxLengthValidator
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


class CourseSerializer(serializers.ModelSerializer):
    instructor = InstructorSerializer(read_only=True)
    title = serializers.CharField(
        validators=[
            MinLengthValidator(3, message="Title must be at least 3 characters long."),
            MaxLengthValidator(150, message="Title cannot exceed 150 characters."),
        ]
    )
    description = serializers.CharField(
        required=True,
        allow_null=False,
        error_messages={
            "required": "Description is required.",
            "blank": "Description cannot be empty.",
        },
    )

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "instructor",
            "published",
            "created_at",
            "updated_at",
        ]


class InstructorCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "published",
            "created_at",
        ]
