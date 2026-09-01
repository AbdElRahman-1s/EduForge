from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.reviews.models import Review

from .models import Category, Course, Lesson, Section, Topic


class CoursePermissionsAndVisibilityTests(APITestCase):
    def setUp(self):
        self.list_url = reverse("course-list")
        self.mine_url = reverse("instructor-courses")

        self.instructor = User.objects.create_user(
            username="instructor_one",
            email="instructor1@example.com",
            password="StrongPassword123!",
            role=User.Role.INSTRUCTOR,
        )
        self.other_instructor = User.objects.create_user(
            username="instructor_two",
            email="instructor2@example.com",
            password="StrongPassword123!",
            role=User.Role.INSTRUCTOR,
        )
        self.student = User.objects.create_user(
            username="student_one",
            email="student1@example.com",
            password="StrongPassword123!",
            role=User.Role.STUDENT,
        )

        self.category = Category.objects.create(name="Programming")
        self.topic = Topic.objects.create(name="Django")

        # Published courses must satisfy the publish invariants (price, thumbnail,
        # at least one topic), otherwise any later update fails re-validation.
        self.published_course = Course.objects.create(
            title="Published course",
            description="Published course description",
            instructor=self.instructor,
            category=self.category,
            level=Course.CourseLevel.BEGINNER,
            price="49.99",
            thumbnail="courses/published.png",
            published=True,
        )
        self.published_course.topics.add(self.topic)

        self.draft_course = Course.objects.create(
            title="Draft course",
            description="Draft course description",
            instructor=self.instructor,
            category=self.category,
            level=Course.CourseLevel.BEGINNER,
            published=False,
        )

        self.other_published_course = Course.objects.create(
            title="Other instructor published course",
            description="Another published course",
            instructor=self.other_instructor,
            category=self.category,
            level=Course.CourseLevel.BEGINNER,
            price="29.99",
            thumbnail="courses/other-published.png",
            published=True,
        )
        self.other_published_course.topics.add(self.topic)

    def _auth_as(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def _course_detail_url(self, course):
        return reverse("course-detail", args=[course.pk])

    def test_public_list_returns_only_published_courses(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

        titles = {course["title"] for course in response.data["results"]}
        self.assertIn(self.published_course.title, titles)
        self.assertIn(self.other_published_course.title, titles)
        self.assertNotIn(self.draft_course.title, titles)

    def test_public_detail_returns_published_course(self):
        response = self.client.get(self._course_detail_url(self.published_course))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.published_course.id)
        self.assertEqual(response.data["title"], self.published_course.title)
        self.assertTrue(response.data["published"])
        self.assertIn("instructor", response.data)

    def test_public_detail_hides_unpublished_course(self):
        response = self.client.get(self._course_detail_url(self.draft_course))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_read_access_is_allowed(self):
        list_response = self.client.get(self.list_url)
        detail_response = self.client.get(
            self._course_detail_url(self.published_course)
        )

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_write_access_is_rejected(self):
        payload = {
            "title": "Unauthenticated course",
            "description": "Course description",
        }
        detail_url = self._course_detail_url(self.published_course)

        responses = [
            self.client.post(self.list_url, payload, format="json"),
            self.client.patch(detail_url, payload, format="json"),
            self.client.delete(detail_url),
        ]

        for response in responses:
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_instructor_cannot_create_courses(self):
        self._auth_as(self.student)
        payload = {
            "title": "Student course",
            "description": "Course description",
        }

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_instructor_can_create_course(self):
        self._auth_as(self.instructor)
        payload = {
            "title": "New instructor course",
            "description": "Course description",
            "category": self.category.id,
            "level": Course.CourseLevel.BEGINNER,
        }

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], payload["title"])
        self.assertTrue(
            Course.objects.filter(
                title=payload["title"], instructor=self.instructor
            ).exists()
        )

    def test_non_owner_cannot_edit_course(self):
        self._auth_as(self.other_instructor)
        payload = {"title": "Updated title"}

        response = self.client.patch(
            self._course_detail_url(self.published_course),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_edit_course(self):
        self._auth_as(self.instructor)
        payload = {"title": "Updated published course title"}

        response = self.client.patch(
            self._course_detail_url(self.published_course),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.published_course.refresh_from_db()
        self.assertEqual(self.published_course.title, payload["title"])

    def test_non_owner_cannot_delete_course(self):
        self._auth_as(self.other_instructor)

        response = self.client.delete(self._course_detail_url(self.published_course))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Course.objects.filter(pk=self.published_course.pk).exists())

    def test_owner_can_delete_course(self):
        self._auth_as(self.instructor)

        response = self.client.delete(self._course_detail_url(self.draft_course))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(pk=self.draft_course.pk).exists())

    def test_instructor_only_mine_endpoint_returns_own_courses(self):
        self._auth_as(self.instructor)

        response = self.client.get(self.mine_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = {course["title"] for course in response.data["results"]}
        self.assertIn(self.published_course.title, titles)
        self.assertIn(self.draft_course.title, titles)
        self.assertNotIn(self.other_published_course.title, titles)

    def test_student_cannot_access_mine_endpoint(self):
        self._auth_as(self.student)

        response = self.client.get(self.mine_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CourseReviewAggregationTests(APITestCase):
    def setUp(self):
        self.list_url = reverse("course-list")
        self.instructor = User.objects.create_user(
            username="review-instructor",
            email="review-instructor@example.com",
            password="StrongPassword123!",
            role=User.Role.INSTRUCTOR,
        )
        self.category = Category.objects.create(name="Aggregation")
        self.topic = Topic.objects.create(name="Reviews")

        self.reviewed_course = Course.objects.create(
            title="Reviewed course",
            description="Course with reviews",
            instructor=self.instructor,
            category=self.category,
            level=Course.CourseLevel.BEGINNER,
            price="19.99",
            thumbnail="courses/reviewed.png",
            published=True,
        )
        self.reviewed_course.topics.add(self.topic)

        self.empty_course = Course.objects.create(
            title="No reviews course",
            description="Course without reviews",
            instructor=self.instructor,
            category=self.category,
            level=Course.CourseLevel.BEGINNER,
            price="19.99",
            thumbnail="courses/empty.png",
            published=True,
        )
        self.empty_course.topics.add(self.topic)

        self.student_one = User.objects.create_user(
            username="reviewer-one", email="reviewer-one@example.com"
        )
        self.student_two = User.objects.create_user(
            username="reviewer-two", email="reviewer-two@example.com"
        )

    def _review(self, student, course, rating):
        return Review.objects.create(student=student, course=course, rating=rating)

    def test_public_list_includes_review_stats(self):
        self._review(self.student_one, self.reviewed_course, rating=4)
        self._review(self.student_two, self.reviewed_course, rating=5)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        by_title = {course["title"]: course for course in response.data["results"]}

        reviewed = by_title[self.reviewed_course.title]
        self.assertEqual(reviewed["review_count"], 2)
        self.assertEqual(reviewed["avg_rating"], 4.5)

        empty = by_title[self.empty_course.title]
        self.assertEqual(empty["review_count"], 0)
        self.assertIsNone(empty["avg_rating"])

    def test_public_detail_includes_review_stats(self):
        self._review(self.student_one, self.reviewed_course, rating=5)

        url = reverse("course-detail", args=[self.reviewed_course.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["review_count"], 1)
        self.assertEqual(response.data["avg_rating"], 5.0)

    def test_detail_without_reviews_returns_zero_and_null(self):
        url = reverse("course-detail", args=[self.empty_course.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["review_count"], 0)
        self.assertIsNone(response.data["avg_rating"])

    def test_review_stats_do_not_inflate_lesson_aggregates(self):
        section = Section.objects.create(
            course=self.reviewed_course, title="Section", order=1
        )
        Lesson.objects.create(
            section=section,
            title="First lesson",
            duration_seconds=120,
            video="https://example.com/first",
            order=1,
        )
        Lesson.objects.create(
            section=section,
            title="Second lesson",
            duration_seconds=300,
            video="https://example.com/second",
            order=2,
        )
        self._review(self.student_one, self.reviewed_course, rating=3)
        self._review(self.student_two, self.reviewed_course, rating=4)

        url = reverse("course-detail", args=[self.reviewed_course.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_lessons"], 2)
        self.assertEqual(response.data["total_duration_seconds"], 420)
        self.assertEqual(response.data["review_count"], 2)
        self.assertEqual(response.data["avg_rating"], 3.5)
