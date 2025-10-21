from rest_framework import serializers

# ----------------- COURSE -----------------
class CourseSerializer(serializers.Serializer):
    _id = serializers.CharField(read_only=True)
    course_title = serializers.CharField(max_length=300)
    course_description = serializers.CharField()
    delivery_mode = serializers.CharField(max_length=50, required=False)
    course_start_date = serializers.DateTimeField()
    course_end_date = serializers.DateTimeField()
    metadata = serializers.DictField()

# ----------------- MODULE -----------------
class ModuleSerializer(serializers.Serializer):
    _id = serializers.CharField(read_only=True)
    course_id = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=200)
    tag = serializers.CharField(max_length=100)

# ----------------- ENROLLMENT -----------------
class EnrollmentSerializer(serializers.Serializer):
    _id = serializers.CharField(read_only=True)
    user_id = serializers.CharField(max_length=100)
    course_id = serializers.CharField(max_length=100)
    status = serializers.CharField(max_length=50, default="enrolled")