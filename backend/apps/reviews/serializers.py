from rest_framework import serializers

from apps.accounts.models import User

from .models import Review


class ReviewerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class ReviewSerializer(serializers.ModelSerializer):
    student = ReviewerSerializer(read_only=True)
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Review
        fields = [
            "id",
            "student",
            "rating",
            "comment",
            "created_at",
        ]
        read_only_fields = ["id", "student", "created_at"]
