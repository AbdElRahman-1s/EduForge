from django.db.models import Avg, Count, IntegerField, OuterRef
from django.db.models.functions import Coalesce

from .models import Review


def annotate_review_stats(queryset):
    """Annotate `review_count` and `avg_rating` onto a Course queryset.

    Both values come from scalar subqueries so they never join the reviews
    table onto the outer query. Joining it alongside the existing
    enrollments/sections/lessons joins would multiply rows and corrupt every
    other aggregate in the query.

    `avg_rating` is NULL when the course has no reviews; `review_count` is 0.
    """
    review_count = (
        Review.objects.filter(course=OuterRef("pk"))
        .values("course")
        .annotate(total=Count("id"))
        .values("total")
    )
    avg_rating = (
        Review.objects.filter(course=OuterRef("pk"))
        .values("course")
        .annotate(avg=Avg("rating"))
        .values("avg")
    )
    return queryset.annotate(
        review_count=Coalesce(review_count, 0, output_field=IntegerField()),
        avg_rating=avg_rating,
    )
