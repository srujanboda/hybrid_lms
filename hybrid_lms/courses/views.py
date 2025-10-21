from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from bson import ObjectId
from rest_framework.permissions import IsAuthenticated
from datetime import datetime


from .mongo_utils import get_db_handle
from .serializers import CourseSerializer, ModuleSerializer, EnrollmentSerializer

db = get_db_handle()
courses_collection = db["courses"]
modules_collection = db["modules"]
enrollments_collection = db["enrollments"]

User = get_user_model()

# ------------------ COURSES ------------------
class CourseCreateView(APIView):
    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            result = courses_collection.insert_one(serializer.validated_data)
            return Response({"message": "Course created successfully", "id": str(result.inserted_id)},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseListView(APIView):
    def get(self, request):
        courses = list(courses_collection.find())
        for c in courses:
            c["_id"] = str(c["_id"])
        return Response(courses, status=status.HTTP_200_OK)


# ------------------ MODULES ------------------
class ModuleCreateView(APIView):
    def post(self, request):
        serializer = ModuleSerializer(data=request.data)
        if serializer.is_valid():
            course_id = serializer.validated_data['course_id']
            if not courses_collection.find_one({"_id": ObjectId(course_id)}):
                return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

            result = modules_collection.insert_one(serializer.validated_data)
            return Response({"message": "Module created", "id": str(result.inserted_id)},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ModuleListView(APIView):
    def get(self, request, course_id):
        modules = list(modules_collection.find({"course_id": course_id}))
        for m in modules:
            m["_id"] = str(m["_id"])
        return Response(modules, status=status.HTTP_200_OK)


# ------------------ ENROLLMENT ------------------
class EnrollmentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            course_id = request.data.get("course_id")

            if not course_id:
                return Response({"error": "course_id is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Check if course exists in MongoDB
            course = courses_collection.find_one({"_id": ObjectId(course_id)})
            if not course:
                return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

            # Check if user is already enrolled
            existing = enrollments_collection.find_one({
                "user_id": user.id,
                "course_id": course_id
            })
            if existing:
                return Response({"message": "User already enrolled in this course."}, status=status.HTTP_200_OK)


            course_title = (
                course.get("title")
                or course.get("course_name")
                or course.get("course_title")
                or "Untitled Course"
            )

            # Create enrollment
            enrollments_collection.insert_one({
                "user_id": user.id,
                "course_id": course_id,
                "course_title": course_title,
                "enrolled_at": datetime.utcnow()
            })

            # Prepare user info
            user_name = getattr(user, "name", None) or getattr(user, "username", None) or user.email

            # Send confirmation email
            email_status = "Email not sent"
            if getattr(user, "email", None):
                subject = f"Enrollment Confirmation - {course_title}"
                message = (
                    f"Hi {user_name},\n\n"
                    f"You have been successfully enrolled in the course '{course_title}'.\n\n"
                    f"Course Description: {course.get('course_description', 'No description provided.')}\n"
                    f"Delivery Mode: {course.get('delivery_mode', 'N/A')}\n"
                    f"Start Date: {course.get('course_start_date', 'Not specified')}\n"
                    f"End Date: {course.get('course_end_date', 'Not specified')}\n\n"
                    f"Thank you for joining Hybrid LMS!"
                )
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                email_status = "Email sent successfully."

            return Response(
                {
                    "message": f"User '{user_name}' successfully enrolled in '{course_title}'.",
                    "email_status": email_status
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)