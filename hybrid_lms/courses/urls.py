from django.urls import path
from .views import (
    CourseCreateView, CourseListView,
    ModuleCreateView, ModuleListView,
    EnrollmentCreateView
)

urlpatterns = [
    path('courses/', CourseListView.as_view(), name='course_list'),
    path('courses/create/', CourseCreateView.as_view(), name='course_create'),
    path('modules/create/', ModuleCreateView.as_view(), name='module_create'),
    path('modules/<str:course_id>/', ModuleListView.as_view(), name='module_list'),
    path('enroll/', EnrollmentCreateView.as_view(), name='enroll_create'),
]
