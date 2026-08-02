from django.urls import path
from .views import (
    CourseListCreateView,
    CourseDetailView,
    InstructorCourseListView,
    CategoryView,
    TopicView,
    SectionView,
    SectionDetailView,
)

urlpatterns = [
    path("courses/", CourseListCreateView.as_view(), name="course-list"),
    path("courses/<int:pk>/", CourseDetailView.as_view(), name="course-detail"),
    path(
        "courses/mine/", InstructorCourseListView.as_view(), name="instructor-courses"
    ),
    path("categories/", CategoryView.as_view(), name="categories-list"),
    path("topics/", TopicView.as_view(), name="topics-list"),
    path(
        "courses/<int:course_id>/sections/",
        SectionView.as_view(),
        name="create-section",
    ),
    path(
        "courses/<int:course_id>/sections/<int:section_id>/",
        SectionDetailView.as_view(),
        name="section-setail",
    ),
]
