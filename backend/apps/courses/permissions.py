from rest_framework.permissions import BasePermission
from accounts.models import User


class IsInstructor(BasePermission):
    message = "Only instructors can perform this action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.user.role == User.Role.INSTRUCTOR
        )


class IsCourseOwner(BasePermission):
    message = "You can only modify your own courses."

    def has_object_permission(self, request, view, obj):
        return obj.instructor == request.user
