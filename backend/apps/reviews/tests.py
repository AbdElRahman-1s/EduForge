from datetime import timedelta

from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.courses.models import Category, Course
from apps.enrollments.models import Enrollment
from apps.reviews.models import Review


class ReviewModelTests(TestCase):
    def setUp(self):
        instructor = User.objects.create_user(
            username="course-owner",
            email="course-owner@example.com",
            role=User.Role.INSTRUCTOR,
        )
        self.category = Category.objects.create(name="Reviews")
        self.course = Course.objects.create(
            instructor=instructor,
            category=self.category,
            title="Reviewable course",
            description="Description",
            level=Course.CourseLevel.BEGINNER,
            price="0.00",
        )
        self.student = User.objects.create_user(
            username="reviewer", email="reviewer@example.com"
        )

    def _create_review(self, **kwargs):
        defaults = {"student": self.student, "course": self.course, "rating": 4}
        defaults.update(kwargs)
        return Review.objects.create(**defaults)

    def test_one_review_per_student_and_course(self):
        self._create_review()
        with self.assertRaises(IntegrityError):
            self._create_review()

    def test_rating_below_one_is_rejected(self):
        with self.assertRaises(IntegrityError):
            self._create_review(rating=0)

    def test_rating_above_five_is_rejected(self):
        with self.assertRaises(IntegrityError):
            self._create_review(rating=6)

    def test_boundary_ratings_are_accepted(self):
        minimum = self._create_review(rating=1)
        other_student = User.objects.create_user(
            username="reviewer-two", email="reviewer-two@example.com"
        )
        maximum = self._create_review(student=other_student, rating=5)

        self.assertEqual(Review.objects.count(), 2)
        self.assertEqual(minimum.rating, 1)
        self.assertEqual(maximum.rating, 5)

    def test_default_ordering_is_newest_first(self):
        student_one = User.objects.create_user(
            username="reviewer-one", email="reviewer-one@example.com"
        )
        student_two = User.objects.create_user(
            username="reviewer-two", email="reviewer-two@example.com"
        )
        student_three = User.objects.create_user(
            username="reviewer-three", email="reviewer-three@example.com"
        )
        oldest = self._create_review(
            student=student_one, comment="oldest", rating=3
        )
        middle = self._create_review(
            student=student_two, comment="middle", rating=4
        )
        newest = self._create_review(
            student=student_three, comment="newest", rating=5
        )

        Review.objects.filter(pk=oldest.pk).update(
            created_at=timezone.now() - timedelta(days=3)
        )
        Review.objects.filter(pk=middle.pk).update(
            created_at=timezone.now() - timedelta(days=2)
        )
        Review.objects.filter(pk=newest.pk).update(
            created_at=timezone.now() - timedelta(days=1)
        )

        self.assertEqual(
            list(Review.objects.values_list("pk", flat=True)),
            [newest.pk, middle.pk, oldest.pk],
        )

    def test_deleting_student_cascades_reviews(self):
        self._create_review()
        self.student.delete()
        self.assertEqual(Review.objects.count(), 0)

    def test_deleting_course_cascades_reviews(self):
        self._create_review()
        self.course.delete()
        self.assertEqual(Review.objects.count(), 0)

    def test_str_representation(self):
        review = self._create_review(rating=5)
        self.assertEqual(str(review), "reviewer rated Reviewable course 5/5")


class ReviewAPITests(APITestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            username="course-owner",
            email="course-owner@example.com",
            role=User.Role.INSTRUCTOR,
        )
        self.category = Category.objects.create(name="Reviews")
        self.course = Course.objects.create(
            instructor=self.instructor,
            category=self.category,
            title="Reviewable course",
            description="Description",
            level=Course.CourseLevel.BEGINNER,
            price="0.00",
            published=True,
        )
        self.student = User.objects.create_user(
            username="reviewer", email="reviewer@example.com"
        )
        self.other_student = User.objects.create_user(
            username="other-reviewer", email="other-reviewer@example.com"
        )
        self.not_enrolled = User.objects.create_user(
            username="not-enrolled", email="not-enrolled@example.com"
        )
        self.list_url = reverse(
            "course-reviews", kwargs={"course_id": self.course.pk}
        )
        self._enroll(self.student)

    def _enroll(self, student, enrollment_status=Enrollment.Status.ACTIVE):
        return Enrollment.objects.create(
            student=student, course=self.course, status=enrollment_status
        )

    def _auth(self, user):
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def _review(self, student, rating=4, comment="Nice"):
        return Review.objects.create(
            student=student, course=self.course, rating=rating, comment=comment
        )

    def _detail_url(self, review):
        return reverse("review-detail", kwargs={"pk": review.pk})

    def test_list_is_public_and_returns_newest_first(self):
        older = self._review(self.student, rating=3, comment="older")
        newer = self._review(self.other_student, rating=5, comment="newer")
        Review.objects.filter(pk=older.pk).update(
            created_at=timezone.now() - timedelta(days=2)
        )

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual([r["id"] for r in results], [newer.pk, older.pk])
        self.assertEqual(results[0]["student"]["username"], self.other_student.username)
        self.assertEqual(results[0]["rating"], 5)

    def test_create_requires_authentication(self):
        response = self.client.post(self.list_url, {"rating": 4}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_actively_enrolled_student_can_create_review(self):
        self._auth(self.student)
        response = self.client.post(
            self.list_url, {"rating": 4, "comment": "Great"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["student"]["username"], self.student.username)
        self.assertEqual(response.data["rating"], 4)
        self.assertEqual(Review.objects.count(), 1)

    def test_student_without_enrollment_cannot_review(self):
        self._auth(self.not_enrolled)
        response = self.client.post(self.list_url, {"rating": 4}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_suspended_enrollment_cannot_review(self):
        self._enroll(self.not_enrolled, Enrollment.Status.SUSPENDED)
        self._auth(self.not_enrolled)
        response = self.client.post(self.list_url, {"rating": 4}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_instructor_cannot_review_own_course(self):
        self._auth(self.instructor)
        response = self.client.post(self.list_url, {"rating": 4}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_review_is_rejected(self):
        self._review(self.student)
        self._auth(self.student)
        response = self.client.post(self.list_url, {"rating": 5}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Review.objects.count(), 1)

    def test_rating_out_of_bounds_is_rejected(self):
        self._auth(self.student)
        low = self.client.post(self.list_url, {"rating": 0}, format="json")
        high = self.client.post(self.list_url, {"rating": 6}, format="json")
        self.assertEqual(low.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(high.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Review.objects.count(), 0)

    def test_author_can_update_review(self):
        review = self._review(self.student, rating=3)
        self._auth(self.student)
        response = self.client.patch(
            self._detail_url(review),
            {"rating": 5, "comment": "Updated"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        review.refresh_from_db()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Updated")

    def test_non_author_cannot_update_review(self):
        review = self._review(self.student, rating=3)
        self._auth(self.other_student)
        response = self.client.patch(
            self._detail_url(review), {"rating": 1}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_update_review(self):
        review = self._review(self.student)
        response = self.client.patch(
            self._detail_url(review), {"rating": 1}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_author_can_delete_review(self):
        review = self._review(self.student)
        self._auth(self.student)
        response = self.client.delete(self._detail_url(review))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Review.objects.count(), 0)

    def test_non_author_cannot_delete_review(self):
        review = self._review(self.student)
        self._auth(self.other_student)
        response = self.client.delete(self._detail_url(review))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Review.objects.count(), 1)

    def test_listing_reviews_for_missing_course_returns_404(self):
        url = reverse("course-reviews", kwargs={"course_id": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_updating_missing_review_returns_404(self):
        self._auth(self.student)
        url = reverse("review-detail", kwargs={"pk": 9999})
        response = self.client.patch(url, {"rating": 2}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_is_paginated_at_five_per_page(self):
        for i in range(12):
            user = User.objects.create_user(
                username=f"paginated-user-{i}",
                email=f"paginated-{i}@example.com",
            )
            self._review(user, rating=4)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 12)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertIsNotNone(response.data["next"])

    def test_load_more_follows_next_link(self):
        for i in range(7):
            user = User.objects.create_user(
                username=f"loadmore-{i}",
                email=f"loadmore-{i}@example.com",
            )
            self._review(user, rating=4)

        first = self.client.get(self.list_url)
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(len(first.data["results"]), 5)
        self.assertIsNotNone(first.data["next"])

        second = self.client.get(first.data["next"])
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(len(second.data["results"]), 2)
        self.assertIsNone(second.data["next"])
