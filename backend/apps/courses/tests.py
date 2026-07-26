from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User

from .models import Course


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

        self.published_course = Course.objects.create(
            title="Published course",
            description="Published course description",
            instructor=self.instructor,
            published=True,
        )
        self.draft_course = Course.objects.create(
            title="Draft course",
            description="Draft course description",
            instructor=self.instructor,
            published=False,
        )
        self.other_published_course = Course.objects.create(
            title="Other instructor published course",
            description="Another published course",
            instructor=self.other_instructor,
            published=True,
        )

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
        }

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], payload["title"])
        self.assertEqual(response.data["instructor"]["id"], self.instructor.id)
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
