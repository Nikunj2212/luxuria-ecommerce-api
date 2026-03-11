from django.contrib.auth.backends import ModelBackend
from .models import User

class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get("email") or kwargs.get("phone")

        user = None

        # 📧 Email login
        if username and "@" in username:
            user = User.objects.filter(email=username).first()

        # 📱 Phone login
        elif username:
            user = User.objects.filter(phone=username).first()

        # 🔐 Password check
        if user and user.check_password(password):
            return user

        return None
