from django.urls import path
from .views import UserRegisterView, UserLoginView
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='user_register'),

    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
            success_url='/api/users/reset/done/'
        ),
        name='password_reset_confirm'
    ),

    # ✅ Add this new URL for "password reset complete"
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]
