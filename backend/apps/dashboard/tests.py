from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.courses.models import Category, Course, Lesson, Section
from apps.enrollments.models import Enrollment


class DashboardOverviewTests(APITestCase):
    def setUp(self):
        self.url = reverse("dashboard-overview")
        self.instructor = self._user("owner", "owner@example.com", User.Role.INSTRUCTOR)
        self.other_instructor = self._user(
            "other-owner", "other-owner@example.com", User.Role.INSTRUCTOR
        )
        self.student = self._user("student", "student@example.com", User.Role.STUDENT)
        self.other_student = self._user(
            "other-student", "other-student@example.com", User.Role.STUDENT
        )
        self.category = Category.objects.create(name="Dashboard")
        self.course = self._course(self.instructor, "Owned course")
        self.other_course = self._course(self.other_instructor, "Foreign course")

    def _user(self, username, email, role):
        return User.objects.create_user(
            username=username, email=email, password=None, role=role
        )

    def _course(self, instructor, title):
        return Course.objects.create(
            instructor=instructor,
            category=self.category,
            title=title,
            description=f"{title} description",
            level=Course.CourseLevel.BEGINNER,
            price="0.00",
        )

    def _auth_as(self, user):
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_anonymous_user_is_rejected(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_is_rejected(self):
        self._auth_as(self.student)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_recent_signups_include_all_statuses_for_owned_courses(self):
        active = Enrollment.objects.create(student=self.student, course=self.course)
        Enrollment.objects.create(
            student=self.other_student,
            course=self.other_course,
        )
        suspended_student = self._user(
            "suspended", "suspended@example.com", User.Role.STUDENT
        )
        Enrollment.objects.create(
            student=suspended_student,
            course=self.course,
            status=Enrollment.Status.SUSPENDED,
        )
        self._auth_as(self.instructor)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["recent_signups"]), 2)
        signups = {signup["id"]: signup for signup in response.data["recent_signups"]}
        self.assertEqual(signups[active.pk]["username"], self.student.username)
        self.assertEqual(signups[active.pk]["email"], self.student.email)
        self.assertEqual(signups[active.pk]["status"], Enrollment.Status.ACTIVE)
        self.assertEqual(
            signups[suspended_student.enrollments.get(course=self.course).pk]["status"],
            Enrollment.Status.SUSPENDED,
        )

    def test_recent_signups_are_newest_first_without_a_count_limit(self):
        enrollments = []
        for index in range(6):
            student = self._user(
                f"student-{index}", f"student-{index}@example.com", User.Role.STUDENT
            )
            enrollment = Enrollment.objects.create(student=student, course=self.course)
            Enrollment.objects.filter(pk=enrollment.pk).update(
                enrolled_at=timezone.now() + timedelta(minutes=index)
            )
            enrollments.append(enrollment)
        self._auth_as(self.instructor)

        response = self.client.get(self.url)

        self.assertEqual(len(response.data["recent_signups"]), 6)
        self.assertEqual(
            [item["id"] for item in response.data["recent_signups"]],
            [item.pk for item in reversed(enrollments)],
        )

    def test_empty_dashboard_returns_empty_recent_signups(self):
        empty_instructor = self._user(
            "empty-owner", "empty-owner@example.com", User.Role.INSTRUCTOR
        )
        self._auth_as(empty_instructor)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["recent_signups"], [])
        self.assertEqual(response.data["recent_courses"], [])
        self.assertEqual(response.data["total_courses"], 0)
        self.assertEqual(response.data["total_students"], 0)

    def test_dashboard_exposes_only_requesting_instructors_data(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        Enrollment.objects.create(student=self.other_student, course=self.other_course)
        self.course.published = True
        self.course.save(update_fields=["published"])
        self.other_course.published = True
        self.other_course.save(update_fields=["published"])
        self._auth_as(self.instructor)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_courses"], 1)
        self.assertEqual(response.data["total_students"], 1)
        self.assertEqual([item["id"] for item in response.data["recent_courses"]], [self.course.pk])
        self.assertEqual([item["username"] for item in response.data["recent_signups"]], [self.student.username])


class InstructorCoursesTests(APITestCase):
    def test_total_duration_is_returned_as_summed_seconds(self):
        instructor = User.objects.create_user(
            username="metrics-owner",
            email="metrics-owner@example.com",
            role=User.Role.INSTRUCTOR,
        )
        category = Category.objects.create(name="Metrics")
        course = Course.objects.create(
            instructor=instructor,
            category=category,
            title="Metrics course",
            description="Description",
            level=Course.CourseLevel.BEGINNER,
            price="0.00",
        )
        section = Section.objects.create(course=course, title="Section", order=1)
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
        token = RefreshToken.for_user(instructor).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(reverse("instructor-courses"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["lesson_count"], 2)
        self.assertEqual(response.data[0]["total_duration"], 420)


class InstructorStudentsTests(APITestCase):
    def setUp(self):
        self.url = reverse("instructor-students")
        self.instructor = self._user(
            "students-owner", "students-owner@example.com", User.Role.INSTRUCTOR
        )
        self.other_instructor = self._user(
            "other-owner", "other-owner-students@example.com", User.Role.INSTRUCTOR
        )
        self.student = self._user(
            "owned-student", "owned-student@example.com", User.Role.STUDENT
        )
        self.foreign_student = self._user(
            "foreign-student", "foreign-student@example.com", User.Role.STUDENT
        )
        self.category = Category.objects.create(name="Student analytics")

    def _user(self, username, email, role):
        return User.objects.create_user(
            username=username, email=email, password=None, role=role
        )

    def _course(self, instructor, title):
        return Course.objects.create(
            instructor=instructor,
            category=self.category,
            title=title,
            description=f"{title} description",
            level=Course.CourseLevel.BEGINNER,
            price="0.00",
        )

    def _auth_as(self, user):
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_returns_each_owned_student_once_with_course_count(self):
        first_course = self._course(self.instructor, "First course")
        second_course = self._course(self.instructor, "Second course")
        foreign_course = self._course(self.other_instructor, "Foreign course")
        first_enrollment = Enrollment.objects.create(
            student=self.student, course=first_course
        )
        latest_enrollment = Enrollment.objects.create(
            student=self.student,
            course=second_course,
            status=Enrollment.Status.SUSPENDED,
        )
        Enrollment.objects.create(
            student=self.foreign_student, course=foreign_course
        )
        latest = timezone.now() + timedelta(minutes=1)
        joined = timezone.now() - timedelta(days=1)
        Enrollment.objects.filter(pk=first_enrollment.pk).update(enrolled_at=joined)
        Enrollment.objects.filter(pk=latest_enrollment.pk).update(enrolled_at=latest)
        self._auth_as(self.instructor)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["username"], self.student.username)
        self.assertEqual(response.data[0]["email"], self.student.email)
        self.assertEqual(response.data[0]["course_count"], 2)
        self.assertEqual(response.data[0]["joined_at"], joined.strftime("%Y:%m:%d"))
        self.assertEqual(set(response.data[0]), {"username", "email", "course_count", "joined_at"})

    def test_anonymous_user_is_rejected(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_user_is_rejected(self):
        self._auth_as(self.student)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
