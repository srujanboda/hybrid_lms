from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.utils import timezone
from django.urls import reverse
from .serializers import UserRegisterSerializer
from .models import User
import secrets

# class UserRegisterView(APIView):
#     def post(self, request):
#         serializer = UserRegisterSerializer(data=request.data)
#         if serializer.is_valid():
#             name = serializer.validated_data['name']
#             email = serializer.validated_data['email']
            
#             # Generate random password
#             password = secrets.token_urlsafe(8)
#             user = User.objects.create_user(email=email, name=name, password=password)
            
#             # Generate password reset link
#             token = default_token_generator.make_token(user)
#             uid = urlsafe_base64_encode(force_bytes(user.pk))
#             reset_link = request.build_absolute_uri(
#                 reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
#             )
            
#             # Send registration email
#             subject = 'Registration Successful'
#             message = f"Hi {name},\n\nYou have successfully registered.\nYour temporary password is: {password}\nPlease reset your password using the following link:\n{reset_link}\nThank you,\nHybrid LMS Team"
#             send_mail(subject, message, None, [email])
            
#             return Response({"message": f"User {name} registered successfully. Email sent.",
#                              "user_id": user.id}, status=status.HTTP_201_CREATED)
            
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# class UserLoginView(APIView):
#     def post(self, request):
#         email = request.data.get('email')
#         password = request.data.get('password')

#         user = authenticate(request, email=email, password=password)
#         if user is not None:
#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 'refresh': str(refresh),
#                 'access': str(refresh.access_token),
#                 'user': {
#                     'id': user.id,
#                     'email': user.email,
#                     'name': user.name,
#                 }
#             })
#         return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.utils import timezone
from django.urls import reverse
from .serializers import UserRegisterSerializer
from .models import User
import secrets

# ------------------ USER REGISTRATION ------------------
class UserRegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data['name']
            email = serializer.validated_data['email']
            
            # Generate random password
            password = secrets.token_urlsafe(8)
            user = User.objects.create_user(email=email, name=name, password=password)
            
            # Send registration email
            subject = 'Registration Successful'
            message = (
                f"Hi {name},\n\nYou have successfully registered.\n"
                f"Your temporary password is: {password}\n"
                f"Please log in and change your password.\n\n"
                f"Thank you,\nHybrid LMS Team"
            )
            send_mail(subject, message, None, [email])
            
            return Response({
                "message": f"User {name} registered successfully. Email sent.",
                "user_id": user.id
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ------------------ LOGIN (STEP 1: SEND OTP) ------------------
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from .models import User

from .utils import send_sms

class UserLoginView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        password = request.data.get('password')

        user = authenticate(request, user_id=user_id, password=password)
        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate OTP
        otp = user.generate_otp()

        # Send Email
        subject = 'Your Hybrid LMS Login Verification Code'
        message = (
            f"Hi {user.user_id},\n\nYour login verification code is: {otp}\n"
            f"This code will expire in 5 minutes.\n\nThank you,\nHybrid LMS Team"
        )
        send_mail(subject, message, None, [user.email])

        # Send SMS (if phone number exists)
        if user.phone_number:
            send_sms(user.phone_number, otp)

        return Response({
            'message': f"OTP sent to {user.email} and {user.phone_number if user.phone_number else 'email only'}. Please verify within 5 minutes."
        }, status=status.HTTP_200_OK)



# ------------------ OTP VERIFICATION (STEP 2: VERIFY OTP & ISSUE TOKEN) ------------------
class VerifyOTPView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        otp = request.data.get('otp')

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if user.verify_otp(otp):
            # Clear OTP after successful verification
            user.otp_code = None
            user.otp_expiry = None
            user.save()

            # Generate tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'OTP verified successfully. Login successful.',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'user_id': user.user_id,
                    'email': user.email,
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
