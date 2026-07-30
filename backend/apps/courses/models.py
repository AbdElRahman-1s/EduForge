from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.db.models.functions import Lower, Trim

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

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


class Course(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses"
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="courses"
    )

    published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
