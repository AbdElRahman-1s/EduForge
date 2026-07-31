from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    CourseSerializer,
    CourseListSerializer,
    CourseDetailSerializer,
    InstructorCourseSerializer,
    CategorySerializer,
    TopicSerializer,
)
from .models import Course, Category, Topic
from .permissions import IsInstructor, IsCourseOwner

# Create your views here.


class CourseListCreateView(generics.ListCreateAPIView):

    def get_queryset(self):
        if self.request.method == "GET":
            return Course.objects.filter(published=True)
        return Course.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CourseListSerializer
        return CourseSerializer

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [IsAuthenticated(), IsInstructor()]


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):

    def get_queryset(self):
        if self.request.method == "GET":
            return Course.objects.filter(published=True)
        return Course.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CourseDetailSerializer
        return CourseSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [IsAuthenticated(), IsInstructor(), IsCourseOwner()]


class InstructorCourseListView(generics.ListAPIView):
    serializer_class = InstructorCourseSerializer
    permission_classes = [IsAuthenticated, IsInstructor]

    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)


class CategoryView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsInstructor]


class TopicView(generics.ListAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticated, IsInstructor]
