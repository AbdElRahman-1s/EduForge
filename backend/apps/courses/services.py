from django.db import transaction
from rest_framework.exceptions import ValidationError

from .models import Section, Lesson


def reorder_sections(course_id: int, instructor, order: list[int]) -> None:
    sections = list(
        Section.objects.filter(
            course_id=course_id,
            course__instructor=instructor,
        )
    )

    expected_ids = {section.id for section in sections}

    if set(order) != expected_ids or len(order) != len(expected_ids):
        raise ValidationError(
            {"order": ["Must include every section ID for this course exactly once."]}
        )

    lookup = {section.id: section for section in sections}

    with transaction.atomic():
        offset = 100000

        for section in sections:
            section.order += offset
        Section.objects.bulk_update(sections, ["order"])

        for new_order, section_id in enumerate(order, start=1):
            lookup[section_id].order = new_order
        Section.objects.bulk_update(sections, ["order"])


def reorder_lessons(section: Section, order: list[int]) -> None:
    lessons = list(Lesson.objects.filter(section=section))
    expected_ids = {lesson.id for lesson in lessons}
    if set(order) != expected_ids or len(order) != len(expected_ids):
        raise ValidationError(
            {"order": ["Must include every lesson ID for this section exactly once."]}
        )

    lookup = {lesson.id: lesson for lesson in lessons}
    with transaction.atomic():
        offset = 100000

        for lesson in lessons:
            lesson.order += offset
        Lesson.objects.bulk_update(lessons, ["order"])

        for new_order, lesson_id in enumerate(order, start=1):
            lookup[lesson_id].order = new_order
        Lesson.objects.bulk_update(lessons, ["order"])
