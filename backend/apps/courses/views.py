from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import CourseCreateSerializer
from .models import Course
from .permissions import IsInstructor

# Create your views here.


class CourseCreateView(generics.CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseCreateSerializer
    permission_classes = [IsAuthenticated, IsInstructor]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)
