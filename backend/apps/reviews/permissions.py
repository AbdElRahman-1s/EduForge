from rest_framework.permissions import BasePermission


class IsReviewAuthor(BasePermission):
    message = "You can only modify your own reviews."

    def has_object_permission(self, request, view, obj):
        return obj.student == request.user
