from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.db.models import Q
from django.db.models.functions import Lower, Trim

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower(Trim("name")), name="unique_lower_trimmed_category_name"
            )
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        return super().save(*args, **kwargs)


class Topic(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower(Trim("name")), name="unique_lower_trimmed_topic_name"
            )
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Course(models.Model):
    class CourseLevel(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"
        ALL = "all", "All Levels"

    class Badge(models.TextChoices):
        BESTSELLER = "bestseller", "Bestseller"
        HOT = "hot", "Hot"
        NEW = "new", "New"
        NONE = "none", "None"

    title = models.CharField(max_length=150)
    description = models.TextField()
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses"
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="courses"
    )

    price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    level = models.CharField(max_length=15, choices=CourseLevel.choices)
    thumbnail = models.ImageField(upload_to="courses/", null=True, blank=True)
    topics = models.ManyToManyField(Topic, related_name="courses")
    badge = models.CharField(max_length=10, choices=Badge.choices, default=Badge.NONE)
    published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(price__gte=0), name="price_must_be_non_negative"
            )
        ]
