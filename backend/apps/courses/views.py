from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import CourseSerializer, InstructorCourseSerializer
from .models import Course
from .permissions import IsInstructor, IsCourseOwner

# Create your views here.


class CourseListCreateView(generics.ListCreateAPIView):
    serializer_class = CourseSerializer

    def get_queryset(self):
        if self.request.method == "GET":
            return Course.objects.filter(published=True)
        return Course.objects.all()

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [IsAuthenticated(), IsInstructor()]


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourseSerializer

    def get_queryset(self):
        if self.request.method == "GET":
            return Course.objects.filter(published=True)
        return Course.objects.all()

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [IsAuthenticated(), IsInstructor(), IsCourseOwner()]


class InstructorCourseListView(generics.ListAPIView):
    serializer_class = InstructorCourseSerializer
    permission_classes = [IsAuthenticated, IsInstructor]

    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)
