from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User

from .models import Category, Course, Lesson, Section, Topic

# The section detail route is registered under this (misspelled) name in urls.py.
SECTION_DETAIL_URL_NAME = "section-setail"


class CurriculumAPITestCase(APITestCase):
    """Shared curriculum fixtures: two instructors, a student, and a course each."""

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Programming")

        cls.instructor = User.objects.create_user(
            username="instructor_one",
            email="instructor1@example.com",
            password="StrongPassword123!",
            role=User.Role.INSTRUCTOR,
        )
        cls.other_instructor = User.objects.create_user(
            username="instructor_two",
            email="instructor2@example.com",
            password="StrongPassword123!",
            role=User.Role.INSTRUCTOR,
        )
        cls.student = User.objects.create_user(
            username="student_one",
            email="student1@example.com",
            password="StrongPassword123!",
            role=User.Role.STUDENT,
        )

        cls.course = cls._create_course(cls.instructor, "Owned course")
        cls.other_course = cls._create_course(
            cls.other_instructor, "Other instructor course"
        )

    # Fixture helpers

    def _auth_as(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    @classmethod
    def _create_course(cls, instructor, title, published=True):
        return Course.objects.create(
            title=title,
            description=f"{title} description",
            instructor=instructor,
            category=cls.category,
            level=Course.CourseLevel.BEGINNER,
            price="49.99",
            published=published,
        )

    def _create_section(self, course, title, order):
        return Section.objects.create(course=course, title=title, order=order)

    def _create_lesson(self, section, title, order, duration_seconds=300, free=False):
        return Lesson.objects.create(
            section=section,
            title=title,
            duration_seconds=duration_seconds,
            video=f"https://cdn.example.com/section-{section.pk}-lesson-{order}.mp4",
            free=free,
            order=order,
        )

    # URL helpers

    def _create_section_url(self, course):
        return reverse("create-section", args=[course.pk])

    def _section_detail_url(self, course, section):
        return reverse(SECTION_DETAIL_URL_NAME, args=[course.pk, section.pk])

    def _create_lesson_url(self, section):
        return reverse("create-lesson", args=[section.pk])

    def _lesson_detail_url(self, section, lesson):
        return reverse("lesson-detail", args=[section.pk, lesson.pk])

    def _reorder_sections_url(self, course):
        return reverse("reorder-sections", args=[course.pk])

    def _reorder_lessons_url(self, section):
        return reverse("reorder-lessons", args=[section.pk])

    def _course_detail_url(self, course):
        return reverse("course-detail", args=[course.pk])


class SectionOwnershipTests(CurriculumAPITestCase):
    """Section CRUD is restricted to the instructor who owns the parent course."""

    def setUp(self):
        super().setUp()
        self.section = self._create_section(self.course, "Getting Started", order=1)
        self.other_section = self._create_section(
            self.other_course, "Other instructor section", order=1
        )

    def test_instructor_can_create_section_for_own_course(self):
        self._auth_as(self.instructor)
        payload = {"title": "Building APIs"}

        response = self.client.post(
            self._create_section_url(self.course), payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], payload["title"])
        self.assertTrue(
            Section.objects.filter(pk=response.data["id"], course=self.course).exists()
        )

    def test_instructor_cannot_create_section_for_another_instructors_course(self):
        """Scoped lookups answer 404 instead of 403 so foreign course IDs stay unconfirmed."""
        self._auth_as(self.instructor)

        response = self.client.post(
            self._create_section_url(self.other_course),
            {"title": "Injected section"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.other_course.sections.count(), 1)

    def test_student_cannot_create_section(self):
        self._auth_as(self.student)

        response = self.client.post(
            self._create_section_url(self.course),
            {"title": "Student section"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_create_section(self):
        response = self.client.post(
            self._create_section_url(self.course),
            {"title": "Anonymous section"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_instructor_can_retrieve_own_section(self):
        self._auth_as(self.instructor)

        response = self.client.get(self._section_detail_url(self.course, self.section))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.section.pk)
        self.assertEqual(response.data["title"], self.section.title)

    def test_instructor_can_update_own_section(self):
        self._auth_as(self.instructor)
        payload = {"title": "Getting Started with Django"}

        response = self.client.patch(
            self._section_detail_url(self.course, self.section), payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.section.refresh_from_db()
        self.assertEqual(self.section.title, payload["title"])

    def test_instructor_cannot_update_another_instructors_section(self):
        self._auth_as(self.instructor)
        original_title = self.other_section.title

        response = self.client.patch(
            self._section_detail_url(self.other_course, self.other_section),
            {"title": "Hijacked title"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.other_section.refresh_from_db()
        self.assertEqual(self.other_section.title, original_title)

    def test_instructor_can_delete_own_section(self):
        self._auth_as(self.instructor)

        response = self.client.delete(
            self._section_detail_url(self.course, self.section)
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Section.objects.filter(pk=self.section.pk).exists())

    def test_instructor_cannot_delete_another_instructors_section(self):
        self._auth_as(self.instructor)

        response = self.client.delete(
            self._section_detail_url(self.other_course, self.other_section)
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Section.objects.filter(pk=self.other_section.pk).exists())

    def test_section_lookup_requires_the_owning_course_in_the_url(self):
        """A section reached through the wrong course ID is not found."""
        self._auth_as(self.instructor)
        second_course = self._create_course(self.instructor, "Second owned course")

        response = self.client.get(
            self._section_detail_url(second_course, self.section)
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_deleting_section_cascades_to_its_lessons(self):
        self._auth_as(self.instructor)
        lesson = self._create_lesson(self.section, "Introduction", order=1)

        self.client.delete(self._section_detail_url(self.course, self.section))

        self.assertFalse(Lesson.objects.filter(pk=lesson.pk).exists())


class LessonOwnershipTests(CurriculumAPITestCase):
    """Lesson CRUD is restricted to the instructor who owns the grandparent course."""

    def setUp(self):
        super().setUp()
        self.section = self._create_section(self.course, "Getting Started", order=1)
        self.other_section = self._create_section(
            self.other_course, "Other instructor section", order=1
        )
        self.lesson = self._create_lesson(self.section, "Introduction", order=1)
        self.other_lesson = self._create_lesson(
            self.other_section, "Other instructor lesson", order=1
        )

        self.lesson_payload = {
            "title": "Environment Setup",
            "video": "https://cdn.example.com/setup.mp4",
            "duration_seconds": 420,
            "free": True,
        }

    def test_instructor_can_create_lesson_in_own_section(self):
        self._auth_as(self.instructor)

        response = self.client.post(
            self._create_lesson_url(self.section), self.lesson_payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], self.lesson_payload["title"])
        self.assertEqual(response.data["duration_seconds"], 420)
        self.assertTrue(response.data["free"])
        self.assertTrue(
            Lesson.objects.filter(
                pk=response.data["id"], section=self.section
            ).exists()
        )

    def test_instructor_cannot_create_lesson_in_another_instructors_section(self):
        self._auth_as(self.instructor)

        response = self.client.post(
            self._create_lesson_url(self.other_section),
            self.lesson_payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.other_section.lessons.count(), 1)

    def test_student_cannot_create_lesson(self):
        self._auth_as(self.student)

        response = self.client.post(
            self._create_lesson_url(self.section), self.lesson_payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_create_lesson(self):
        response = self.client.post(
            self._create_lesson_url(self.section), self.lesson_payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_instructor_can_retrieve_own_lesson(self):
        self._auth_as(self.instructor)

        response = self.client.get(self._lesson_detail_url(self.section, self.lesson))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.lesson.pk)
        self.assertEqual(response.data["video"], self.lesson.video)

    def test_instructor_can_update_own_lesson(self):
        self._auth_as(self.instructor)

        response = self.client.patch(
            self._lesson_detail_url(self.section, self.lesson),
            {"free": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertTrue(self.lesson.free)

    def test_instructor_cannot_update_another_instructors_lesson(self):
        self._auth_as(self.instructor)
        original_title = self.other_lesson.title

        response = self.client.patch(
            self._lesson_detail_url(self.other_section, self.other_lesson),
            {"title": "Hijacked lesson"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.other_lesson.refresh_from_db()
        self.assertEqual(self.other_lesson.title, original_title)

    def test_instructor_can_delete_own_lesson(self):
        self._auth_as(self.instructor)

        response = self.client.delete(
            self._lesson_detail_url(self.section, self.lesson)
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(pk=self.lesson.pk).exists())

    def test_instructor_cannot_delete_another_instructors_lesson(self):
        self._auth_as(self.instructor)

        response = self.client.delete(
            self._lesson_detail_url(self.other_section, self.other_lesson)
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Lesson.objects.filter(pk=self.other_lesson.pk).exists())

    def test_lesson_lookup_requires_the_owning_section_in_the_url(self):
        """A lesson reached through the wrong section ID is not found."""
        self._auth_as(self.instructor)
        second_section = self._create_section(self.course, "Building APIs", order=2)

        response = self.client.get(
            self._lesson_detail_url(second_section, self.lesson)
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_cannot_be_set_through_the_api(self):
        """`order` is read-only; it is owned by creation and the reorder endpoints."""
        self._auth_as(self.instructor)

        response = self.client.patch(
            self._lesson_detail_url(self.section, self.lesson),
            {"order": 99},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.order, 1)


class SectionOrderingTests(CurriculumAPITestCase):
    """New sections are appended; ordering is only rewritten by the reorder endpoint."""

    def setUp(self):
        super().setUp()
        self._auth_as(self.instructor)

    def _post_section(self, course, title):
        return self.client.post(
            self._create_section_url(course), {"title": title}, format="json"
        )

    def test_first_section_receives_order_one(self):
        response = self._post_section(self.course, "Getting Started")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["order"], 1)

    def test_sections_are_appended_in_creation_order(self):
        titles = ["Getting Started", "Building APIs", "Deployment"]

        for title in titles:
            self._post_section(self.course, title)

        self.assertEqual(
            list(self.course.sections.values_list("title", "order")),
            [(title, index) for index, title in enumerate(titles, start=1)],
        )

    def test_section_order_is_scoped_per_course(self):
        self._post_section(self.course, "Getting Started")
        second_course = self._create_course(self.instructor, "Second owned course")

        response = self._post_section(second_course, "Its own first section")

        self.assertEqual(response.data["order"], 1)

    def test_deleting_a_section_leaves_a_gap_and_the_next_one_appends_after_the_max(
        self,
    ):
        """Orders are never renumbered on delete; new sections append after the highest."""
        self._create_section(self.course, "Getting Started", order=1)
        removable = self._create_section(self.course, "Building APIs", order=2)
        self._create_section(self.course, "Deployment", order=3)
        self.client.delete(self._section_detail_url(self.course, removable))

        response = self._post_section(self.course, "Monitoring")

        self.assertEqual(response.data["order"], 4)
        self.assertEqual(
            list(self.course.sections.values_list("order", flat=True)), [1, 3, 4]
        )

    def test_reorder_sections_rewrites_order_contiguously(self):
        first = self._create_section(self.course, "Getting Started", order=1)
        second = self._create_section(self.course, "Building APIs", order=2)
        third = self._create_section(self.course, "Deployment", order=3)

        response = self.client.patch(
            self._reorder_sections_url(self.course),
            {"order": [third.pk, first.pk, second.pk]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Sections reordered successfully.")
        self.assertEqual(
            list(self.course.sections.values_list("pk", flat=True)),
            [third.pk, first.pk, second.pk],
        )
        for section, expected_order in ((third, 1), (first, 2), (second, 3)):
            section.refresh_from_db()
            self.assertEqual(section.order, expected_order)

    def test_reorder_sections_rejects_a_duplicate_alongside_the_full_set(self):
        """Every ID is present, so only the length check can catch the repeat."""
        first = self._create_section(self.course, "Getting Started", order=1)
        second = self._create_section(self.course, "Building APIs", order=2)

        response = self.client.patch(
            self._reorder_sections_url(self.course),
            {"order": [first.pk, second.pk, second.pk]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("order", response.data)

    def test_reorder_sections_rejects_missing_ids(self):
        first = self._create_section(self.course, "Getting Started", order=1)
        second = self._create_section(self.course, "Building APIs", order=2)

        response = self.client.patch(
            self._reorder_sections_url(self.course),
            {"order": [first.pk]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        second.refresh_from_db()
        self.assertEqual(second.order, 2)

    def test_reorder_sections_rejects_ids_from_another_course(self):
        """The count is right, so the foreign ID alone is what makes this invalid."""
        first = self._create_section(self.course, "Getting Started", order=1)
        second = self._create_section(self.course, "Building APIs", order=2)
        foreign = self._create_section(self.other_course, "Foreign section", order=1)

        response = self.client.patch(
            self._reorder_sections_url(self.course),
            {"order": [first.pk, foreign.pk]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for section, expected_order in ((first, 1), (second, 2), (foreign, 1)):
            section.refresh_from_db()
            self.assertEqual(section.order, expected_order)

    def test_reorder_sections_rejects_empty_payload(self):
        self._create_section(self.course, "Getting Started", order=1)

        response = self.client.patch(
            self._reorder_sections_url(self.course), {"order": []}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reorder_sections_rejects_another_instructors_course(self):
        """Ownership scoping leaves no sections to match, so the payload is rejected."""
        foreign = self._create_section(self.other_course, "Foreign section", order=1)

        response = self.client.patch(
            self._reorder_sections_url(self.other_course),
            {"order": [foreign.pk]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        foreign.refresh_from_db()
        self.assertEqual(foreign.order, 1)

    def test_student_cannot_reorder_sections(self):
        self._create_section(self.course, "Getting Started", order=1)
        self._auth_as(self.student)

        response = self.client.patch(
            self._reorder_sections_url(self.course), {"order": [1]}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LessonOrderingTests(CurriculumAPITestCase):
    """New lessons are appended within their section; reordering is section-scoped."""

    def setUp(self):
        super().setUp()
        self.section = self._create_section(self.course, "Getting Started", order=1)
        self._auth_as(self.instructor)

    def _post_lesson(self, section, title):
        return self.client.post(
            self._create_lesson_url(section),
            {
                "title": title,
                "video": "https://cdn.example.com/lesson.mp4",
                "duration_seconds": 300,
            },
            format="json",
        )

    def test_first_lesson_receives_order_one(self):
        response = self._post_lesson(self.section, "Introduction")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["order"], 1)

    def test_lessons_are_appended_in_creation_order(self):
        titles = ["Introduction", "Environment Setup", "First Endpoint"]

        for title in titles:
            self._post_lesson(self.section, title)

        self.assertEqual(
            list(self.section.lessons.values_list("title", "order")),
            [(title, index) for index, title in enumerate(titles, start=1)],
        )

    def test_lesson_order_is_scoped_per_section(self):
        self._post_lesson(self.section, "Introduction")
        second_section = self._create_section(self.course, "Building APIs", order=2)

        response = self._post_lesson(second_section, "Its own first lesson")

        self.assertEqual(response.data["order"], 1)

    def test_deleting_a_lesson_leaves_a_gap_and_the_next_one_appends_after_the_max(self):
        self._create_lesson(self.section, "Introduction", order=1)
        removable = self._create_lesson(self.section, "Environment Setup", order=2)
        self._create_lesson(self.section, "First Endpoint", order=3)
        self.client.delete(self._lesson_detail_url(self.section, removable))

        response = self._post_lesson(self.section, "Testing")

        self.assertEqual(response.data["order"], 4)
        self.assertEqual(
            list(self.section.lessons.values_list("order", flat=True)), [1, 3, 4]
        )

    def test_reorder_lessons_rewrites_order_contiguously(self):
        first = self._create_lesson(self.section, "Introduction", order=1)
        second = self._create_lesson(self.section, "Environment Setup", order=2)
        third = self._create_lesson(self.section, "First Endpoint", order=3)

        response = self.client.patch(
            self._reorder_lessons_url(self.section),
            {"order": [third.pk, first.pk, second.pk]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Lessons reordered successfully.")
        self.assertEqual(
            list(self.section.lessons.values_list("pk", flat=True)),
            [third.pk, first.pk, second.pk],
        )
        for lesson, expected_order in ((third, 1), (first, 2), (second, 3)):
            lesson.refresh_from_db()
            self.assertEqual(lesson.order, expected_order)

    def test_reorder_lessons_rejects_a_duplicate_alongside_the_full_set(self):
        """Every ID is present, so only the length check can catch the repeat."""
        first = self._create_lesson(self.section, "Introduction", order=1)
        second = self._create_lesson(self.section, "Environment Setup", order=2)

        response = self.client.patch(
            self._reorder_lessons_url(self.section),
            {"order": [first.pk, second.pk, second.pk]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("order", response.data)

    def test_reorder_lessons_rejects_missing_ids(self):
        first = self._create_lesson(self.section, "Introduction", order=1)
        second = self._create_lesson(self.section, "Environment Setup", order=2)

        response = self.client.patch(
            self._reorder_lessons_url(self.section),
            {"order": [first.pk]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        second.refresh_from_db()
        self.assertEqual(second.order, 2)

    def test_reorder_lessons_rejects_ids_from_another_section(self):
        """The count is right, so the foreign ID alone is what makes this invalid."""
        first = self._create_lesson(self.section, "Introduction", order=1)
        second = self._create_lesson(self.section, "Environment Setup", order=2)
        second_section = self._create_section(self.course, "Building APIs", order=2)
        foreign = self._create_lesson(second_section, "Foreign lesson", order=1)

        response = self.client.patch(
            self._reorder_lessons_url(self.section),
            {"order": [first.pk, foreign.pk]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for lesson, expected_order in ((first, 1), (second, 2), (foreign, 1)):
            lesson.refresh_from_db()
            self.assertEqual(lesson.order, expected_order)

    def test_reorder_lessons_rejects_another_instructors_section(self):
        other_section = self._create_section(
            self.other_course, "Other instructor section", order=1
        )
        foreign = self._create_lesson(other_section, "Foreign lesson", order=1)

        response = self.client.patch(
            self._reorder_lessons_url(other_section),
            {"order": [foreign.pk]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        foreign.refresh_from_db()
        self.assertEqual(foreign.order, 1)

    def test_student_cannot_reorder_lessons(self):
        lesson = self._create_lesson(self.section, "Introduction", order=1)
        self._auth_as(self.student)

        response = self.client.patch(
            self._reorder_lessons_url(self.section),
            {"order": [lesson.pk]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CourseDetailCurriculumTests(CurriculumAPITestCase):
    """The public course details endpoint exposes the full curriculum outline.

    Sections, lesson titles and lesson durations are always visible. Only the
    `video` of a free-preview lesson is revealed; locked lessons return null.
    """

    def setUp(self):
        super().setUp()

        # Created back-to-front so response ordering cannot pass on insertion order.
        self.second_section = self._create_section(self.course, "Building APIs", order=2)
        self.first_section = self._create_section(
            self.course, "Getting Started", order=1
        )

        self.locked_lesson = self._create_lesson(
            self.first_section, "Environment Setup", order=2, duration_seconds=420
        )
        self.free_lesson = self._create_lesson(
            self.first_section,
            "Introduction",
            order=1,
            duration_seconds=180,
            free=True,
        )
        self._create_lesson(
            self.second_section, "Models", order=1, duration_seconds=600
        )
        self._create_lesson(
            self.second_section, "Serializers", order=2, duration_seconds=720
        )

        self.detail_url = self._course_detail_url(self.course)

    def _get_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data

    def _lessons_by_title(self, data):
        return {
            lesson["title"]: lesson
            for section in data["sections"]
            for lesson in section["lessons"]
        }

    # Anonymous visibility

    def test_anonymous_receives_all_sections(self):
        data = self._get_detail()

        self.assertEqual(
            [section["title"] for section in data["sections"]],
            ["Getting Started", "Building APIs"],
        )

    def test_anonymous_receives_all_lesson_titles(self):
        data = self._get_detail()

        self.assertEqual(
            set(self._lessons_by_title(data)),
            {"Introduction", "Environment Setup", "Models", "Serializers"},
        )

    def test_anonymous_receives_all_lesson_durations(self):
        data = self._get_detail()

        durations = {
            title: lesson["duration_seconds"]
            for title, lesson in self._lessons_by_title(data).items()
        }
        self.assertEqual(
            durations,
            {
                "Introduction": 180,
                "Environment Setup": 420,
                "Models": 600,
                "Serializers": 720,
            },
        )

    def test_anonymous_sees_video_url_for_free_lesson(self):
        data = self._get_detail()

        lesson = self._lessons_by_title(data)["Introduction"]
        self.assertTrue(lesson["free"])
        self.assertEqual(lesson["video"], self.free_lesson.video)

    def test_anonymous_sees_null_video_for_locked_lesson(self):
        data = self._get_detail()

        lesson = self._lessons_by_title(data)["Environment Setup"]
        self.assertFalse(lesson["free"])
        self.assertIsNone(lesson["video"])

    def test_non_enrolled_student_sees_the_same_video_visibility(self):
        self._auth_as(self.student)

        lessons = self._lessons_by_title(self._get_detail())

        self.assertEqual(lessons["Introduction"]["video"], self.free_lesson.video)
        self.assertIsNone(lessons["Environment Setup"]["video"])

    def test_enrolled_student_sees_all_lesson_videos(self):
        from apps.enrollments.models import Enrollment

        Enrollment.objects.create(student=self.student, course=self.course)
        self._auth_as(self.student)

        lessons = self._lessons_by_title(self._get_detail())

        self.assertEqual(lessons["Introduction"]["video"], self.free_lesson.video)
        self.assertEqual(lessons["Environment Setup"]["video"], self.locked_lesson.video)

    def test_course_owner_sees_all_lesson_videos(self):
        self._auth_as(self.instructor)

        lessons = self._lessons_by_title(self._get_detail())

        self.assertEqual(lessons["Introduction"]["video"], self.free_lesson.video)
        self.assertEqual(lessons["Environment Setup"]["video"], self.locked_lesson.video)

    def test_enrollment_visibility_does_not_leak_between_users(self):
        from apps.enrollments.models import Enrollment

        Enrollment.objects.create(student=self.student, course=self.course)
        self._auth_as(self.student)
        enrolled_lessons = self._lessons_by_title(self._get_detail())

        self._auth_as(self.other_instructor)
        non_enrolled_lessons = self._lessons_by_title(self._get_detail())

        self.assertEqual(
            enrolled_lessons["Environment Setup"]["video"], self.locked_lesson.video
        )
        self.assertIsNone(non_enrolled_lessons["Environment Setup"]["video"])

    def test_locked_video_url_is_absent_from_the_raw_response_body(self):
        """The locked URL must not leak anywhere in the payload, not just be nulled."""
        response = self.client.get(self.detail_url)

        self.assertNotContains(response, self.locked_lesson.video)

    # Ordering in the response

    def test_sections_are_ordered_by_order_field(self):
        data = self._get_detail()

        self.assertEqual(
            [section["order"] for section in data["sections"]],
            [1, 2],
        )
        self.assertEqual(data["sections"][0]["id"], self.first_section.pk)

    def test_lessons_are_ordered_by_order_field_within_each_section(self):
        data = self._get_detail()

        self.assertEqual(
            [
                [lesson["title"] for lesson in section["lessons"]]
                for section in data["sections"]
            ],
            [["Introduction", "Environment Setup"], ["Models", "Serializers"]],
        )

    def test_reordering_sections_is_reflected_in_course_details(self):
        self._auth_as(self.instructor)
        self.client.patch(
            self._reorder_sections_url(self.course),
            {"order": [self.second_section.pk, self.first_section.pk]},
            format="json",
        )
        self.client.credentials()

        data = self._get_detail()

        self.assertEqual(
            [section["title"] for section in data["sections"]],
            ["Building APIs", "Getting Started"],
        )

    # Computed metadata

    def test_total_lessons_counts_every_lesson_in_the_course(self):
        data = self._get_detail()

        self.assertEqual(data["total_lessons"], 4)

    def test_total_duration_seconds_sums_every_lesson_duration(self):
        data = self._get_detail()

        self.assertEqual(data["total_duration_seconds"], 180 + 420 + 600 + 720)

    def test_metadata_ignores_lessons_from_other_courses(self):
        other_section = self._create_section(
            self.other_course, "Other instructor section", order=1
        )
        self._create_lesson(
            other_section, "Unrelated lesson", order=1, duration_seconds=9999
        )

        data = self._get_detail()

        self.assertEqual(data["total_lessons"], 4)
        self.assertEqual(data["total_duration_seconds"], 180 + 420 + 600 + 720)

    def test_metadata_is_not_inflated_by_multiple_topics(self):
        """Guards against join fanout between the topics M2M and the lesson aggregates."""
        self.course.topics.add(
            Topic.objects.create(name="Python"),
            Topic.objects.create(name="Django"),
        )

        data = self._get_detail()

        self.assertEqual(data["total_lessons"], 4)
        self.assertEqual(data["total_duration_seconds"], 180 + 420 + 600 + 720)

    def test_metadata_is_zero_for_a_course_without_lessons(self):
        empty_course = self._create_course(self.instructor, "Empty course")

        response = self.client.get(self._course_detail_url(empty_course))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["sections"], [])
        self.assertEqual(response.data["total_lessons"], 0)
        self.assertEqual(response.data["total_duration_seconds"], 0)

    def test_section_without_lessons_is_returned_with_an_empty_lesson_list(self):
        empty_section = self._create_section(self.course, "Coming Soon", order=3)

        data = self._get_detail()

        section = next(
            item for item in data["sections"] if item["id"] == empty_section.pk
        )
        self.assertEqual(section["lessons"], [])
        self.assertEqual(data["total_lessons"], 4)


class UnpublishedCourseCurriculumAccessTests(CurriculumAPITestCase):
    """Draft curricula are readable by their owner only."""

    def setUp(self):
        super().setUp()
        self.draft_course = self._create_course(
            self.instructor, "Draft course", published=False
        )
        self.draft_section = self._create_section(
            self.draft_course, "Draft section", order=1
        )
        self._create_lesson(self.draft_section, "Draft lesson", order=1)

        self.draft_url = self._course_detail_url(self.draft_course)

    def test_owner_can_retrieve_own_unpublished_course_with_curriculum(self):
        self._auth_as(self.instructor)

        response = self.client.get(self.draft_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["published"])
        self.assertEqual(
            [section["title"] for section in response.data["sections"]],
            ["Draft section"],
        )
        self.assertEqual(response.data["total_lessons"], 1)

    def test_anonymous_receives_404_for_unpublished_course(self):
        response = self.client.get(self.draft_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_receives_404_for_unpublished_course(self):
        self._auth_as(self.student)

        response = self.client.get(self.draft_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_other_instructor_receives_404_for_unpublished_course(self):
        self._auth_as(self.other_instructor)

        response = self.client.get(self.draft_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
