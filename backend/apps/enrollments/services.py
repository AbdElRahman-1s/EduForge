from .models import Enrollment


def is_enrolled(user, course):
    """True when `user` has an active enrollment in `course`."""
    if not getattr(user, "is_authenticated", False):
        return False
    return Enrollment.objects.filter(
        student=user, course=course, status=Enrollment.Status.ACTIVE
    ).exists()


def active_course_ids(user):
    """Course ids where `user` holds an active enrollment."""
    return user.enrollments.filter(status=Enrollment.Status.ACTIVE).values_list(
        "course_id", flat=True
    )
