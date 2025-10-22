from django.contrib.auth.backends import ModelBackend
from .models import User

class UserIDBackend(ModelBackend):
    def authenticate(self, request, user_id=None, password=None, **kwargs):
        try:
            user = User.objects.get(user_id=user_id)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
