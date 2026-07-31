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
    topics = serializers.PrimaryKeyRelatedField(
        required=False, queryset=Topic.objects.all(), many=True
    )

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "category",
            "level",
            "price",
            "thumbnail",
            "topics",
            "badge",
            "published",
        ]

    def validate(self, attrs):
        instance = getattr(self, "instance", None)

        is_published = attrs.get("published", instance.published if instance else False)

        if is_published:
            errors = {}

            price = attrs.get("price", getattr(instance, "price", None))
            thumbnail = attrs.get("thumbnail", getattr(instance, "thumbnail", None))

            if "topics" in attrs:
                has_topics = bool(attrs["topics"])
            elif instance:
                has_topics = instance.topics.exists()
            else:
                has_topics = False

            if price is None:
                errors["price"] = ["Price is required to publish the course."]

            if not thumbnail:
                errors["thumbnail"] = ["A thumbnail is required to publish the course."]

            if not has_topics:
                errors["topics"] = ["At least one topic must be selected to publish."]

            if errors:
                raise serializers.ValidationError(errors)

        return attrs


class CourseListSerializer(serializers.ModelSerializer):
    category = serializers.ReadOnlyField(source="category.name")
    topics = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)
    instructor = InstructorSerializer(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "category",
            "level",
            "price",
            "thumbnail",
            "topics",
            "badge",
            "instructor",
            "published",
            "created_at",
        ]


class CourseDetailSerializer(CourseListSerializer):
    class Meta(CourseListSerializer.Meta):
        fields = CourseListSerializer.Meta.fields + ["description"]


class InstructorCourseSerializer(CourseListSerializer):
    pass
