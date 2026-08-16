from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.courses.models import Category, Course, Lesson, Section, Topic

from .models import Enrollment


class EnrollmentTestDataMixin:
    def setUp(self):
        super().setUp()
        self.instructor = self._create_user(
            "owner", "owner@example.com", User.Role.INSTRUCTOR
        )
        self.other_instructor = self._create_user(
            "other-owner", "other-owner@example.com", User.Role.INSTRUCTOR
        )
        self.student = self._create_user(
            "student", "student@example.com", User.Role.STUDENT
        )
        self.other_student = self._create_user(
            "other-student", "other-student@example.com", User.Role.STUDENT
        )
        self.category = Category.objects.create(name="Development")
        self.topic = Topic.objects.create(name="Testing")
        self.free_course = self._create_course(self.instructor, "Free course")

    def _create_user(self, username, email, role):
        return User.objects.create_user(
            username=username, email=email, password=None, role=role
        )

    def _create_course(
        self, instructor, title, *, price="0.00", published=True, badge=Course.Badge.NEW
    ):
        course = Course.objects.create(
            title=title,
            description=f"{title} description",
            instructor=instructor,
            category=self.category,
            level=Course.CourseLevel.BEGINNER,
            price=price,
            thumbnail=f"courses/{title.lower().replace(' ', '-')}.png",
            badge=badge,
            published=published,
        )
        course.topics.add(self.topic)
        return course

    def _auth_as(self, user):
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def _enroll_url(self, course):
        return reverse("enroll", args=[course.pk])


class EnrollmentCreateAPITests(EnrollmentTestDataMixin, APITestCase):
    def test_anonymous_user_cannot_enroll(self):
        response = self.client.post(self._enroll_url(self.free_course), {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Enrollment.objects.exists())

    def test_student_can_enroll_in_free_published_course(self):
        self._auth_as(self.student)

        response = self.client.post(self._enroll_url(self.free_course), {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["course_id"], self.free_course.pk)
        self.assertTrue(
            Enrollment.objects.filter(student=self.student, course=self.free_course).exists()
        )

    def test_duplicate_enrollment_is_rejected(self):
        Enrollment.objects.create(student=self.student, course=self.free_course)
        self._auth_as(self.student)

        response = self.client.post(self._enroll_url(self.free_course), {}, format="json")

        self.assertIn(
            response.status_code,
            (status.HTTP_400_BAD_REQUEST, status.HTTP_409_CONFLICT),
        )
        self.assertEqual(
            Enrollment.objects.filter(student=self.student, course=self.free_course).count(),
            1,
        )

    def test_unpublished_course_is_rejected(self):
        draft = self._create_course(self.instructor, "Draft", published=False)
        self._auth_as(self.student)

        response = self.client.post(self._enroll_url(draft), {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Enrollment.objects.filter(student=self.student, course=draft).exists())

    def test_paid_course_is_rejected(self):
        paid = self._create_course(self.instructor, "Paid", price="19.99")
        self._auth_as(self.student)

        response = self.client.post(self._enroll_url(paid), {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Enrollment.objects.filter(student=self.student, course=paid).exists())

    def test_student_id_in_payload_cannot_enroll_another_user(self):
        self._auth_as(self.student)

        response = self.client.post(
            self._enroll_url(self.free_course),
            {"student": self.other_student.pk, "student_id": self.other_student.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        enrollment = Enrollment.objects.get(course=self.free_course)
        self.assertEqual(enrollment.student_id, self.student.pk)
        self.assertNotEqual(enrollment.student_id, self.other_student.pk)

    def test_instructor_cannot_enroll_in_own_course(self):
        self._auth_as(self.instructor)

        response = self.client.post(self._enroll_url(self.free_course), {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Enrollment.objects.exists())

    def test_instructor_can_enroll_in_another_instructors_free_published_course(self):
        course = self._create_course(self.other_instructor, "Peer course")
        self._auth_as(self.instructor)

        response = self.client.post(self._enroll_url(course), {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Enrollment.objects.filter(student=self.instructor, course=course).exists()
        )


class EnrollmentConstraintTests(EnrollmentTestDataMixin, TestCase):
    def test_database_rejects_duplicate_student_course_pair(self):
        Enrollment.objects.create(student=self.student, course=self.free_course)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Enrollment.objects.create(student=self.student, course=self.free_course)

        self.assertEqual(Enrollment.objects.count(), 1)


class MyLearningAPITests(EnrollmentTestDataMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.mine_url = reverse("my-enrollments")

    def test_returns_only_requesting_users_enrollments(self):
        own = Enrollment.objects.create(student=self.student, course=self.free_course)
        other_course = self._create_course(self.other_instructor, "Other course")
        Enrollment.objects.create(student=self.other_student, course=other_course)
        self._auth_as(self.student)

        response = self.client.get(self.mine_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], own.course_id)
        self.assertNotIn(other_course.pk, [item["id"] for item in response.data["results"]])

    def test_response_contains_expected_lightweight_course_data(self):
        section = Section.objects.create(course=self.free_course, title="Start", order=1)
        Lesson.objects.create(
            section=section,
            title="Welcome",
            duration_seconds=125,
            video="https://example.com/welcome",
            order=1,
        )
        enrollment = Enrollment.objects.create(student=self.student, course=self.free_course)
        self._auth_as(self.student)

        response = self.client.get(self.mine_url)

        item = response.data["results"][0]
        self.assertEqual(
            set(item),
            {
                "id", "title", "thumbnail", "badge", "category", "level",
                "total_lessons", "total_duration_seconds", "instructor",
                "enrolled_at", "progress_percent",
            },
        )
        self.assertEqual(item["id"], self.free_course.pk)
        self.assertEqual(item["title"], self.free_course.title)
        self.assertEqual(item["category"], self.category.name)
        self.assertEqual(item["total_lessons"], 1)
        self.assertEqual(item["total_duration_seconds"], 125)
        self.assertEqual(item["instructor"]["id"], self.instructor.pk)
        self.assertEqual(item["progress_percent"], 0)
        self.assertEqual(item["enrolled_at"], enrollment.enrolled_at.isoformat().replace("+00:00", "Z"))

    def test_empty_enrollment_list(self):
        self._auth_as(self.student)

        response = self.client.get(self.mine_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"count": 0, "results": []})

    def test_query_count_does_not_grow_with_related_course_data(self):
        first = self.free_course
        second = self._create_course(self.other_instructor, "Second course")
        Enrollment.objects.create(student=self.student, course=first)
        Enrollment.objects.create(student=self.student, course=second)
        self._auth_as(self.student)

        # JWT authentication loads the requester once; all enrollments and their
        # lightweight course data are then returned by one joined aggregate query.
        with self.assertNumQueries(2):
            response = self.client.get(self.mine_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
