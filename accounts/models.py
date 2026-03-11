from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import random

class UserManager(BaseUserManager):
    def create_user(self, email, phone, password=None):
        if not email:
            raise ValueError("Email required")
        if not phone:
            raise ValueError("Phone required")

        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, password):
        user = self.create_user(email, phone, password)
        user.is_staff = True
        user.is_superuser = True
        user.profile_completed = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    date_joined = models.DateTimeField(default=timezone.now)
    username = models.CharField(max_length=150, blank=True)  # NOT UNIQUE
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    profile_completed = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    objects = UserManager()

    def __str__(self):
        return self.email

class Address(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    house_no = models.CharField(max_length=100)
    address_line1 = models.CharField(max_length=255)
    landmark = models.CharField(max_length=255)
    area = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.user.email} Address"


class PasswordOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.save()