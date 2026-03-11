from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import UserLoginActivity
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(user_logged_in)
def save_user_login(sender, request, user, **kwargs):
    ip = request.META.get("REMOTE_ADDR")
    UserLoginActivity.objects.create(
        user=user,
        ip_address=ip
    )

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)