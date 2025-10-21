from django.urls import path
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegisterView,
    UserLoginView,
    VerifyOTPView,
)

urlpatterns = [
    # -------- User Registration --------
    path('register/', UserRegisterView.as_view(), name='user_register'),

    # -------- Step 1: Login (Send OTP) --------
    path('login/', UserLoginView.as_view(), name='user_login'),

    # -------- Step 2: Verify OTP (Get Tokens) --------
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),

    # -------- JWT Token Refresh --------
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # -------- Password Reset (Optional for registration email reset link) --------
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
            success_url='/api/users/reset/done/'
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='password_reset_complete',
    ),
]
