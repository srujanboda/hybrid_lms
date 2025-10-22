from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from datetime import timedelta
import random
from django.core.validators import RegexValidator



class UserManager(BaseUserManager):
    def create_user(self, user_id, email, password=None, **extra_fields):
        if not user_id:
            raise ValueError('The user_id field must be set')
        if not email:
            raise ValueError('The email field must be set')

        email = self.normalize_email(email)
        user = self.model(user_id=user_id, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(user_id, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, validators=[RegexValidator(
            regex=r'^\+?\d{10,15}$',
            message="Enter a valid phone number."
        )],
        blank=True,
        null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['email', 'phone_number']

    def __str__(self):
        return self.user_id

    def generate_otp(self):
        self.otp_code = str(random.randint(100000, 999999))
        self.otp_expiry = timezone.now() + timedelta(minutes=5)
        self.save()
        return self.otp_code

    def verify_otp(self, otp):
        return self.otp_code == otp and self.otp_expiry and self.otp_expiry > timezone.now()

