from django.conf import settings
from django.db import models


# ---- STATUS OPTIONS ----
STATUS_CHOICES = (
    ('open', 'Open'),
    ('closed', 'Closed'),
)


class ContactThread(models.Model):

    user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="contact_threads"   # 🔥 ADD THIS
)
    guest_name = models.CharField(max_length=200, null=True, blank=True)
    guest_email = models.EmailField(null=True, blank=True)

    subject = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    # 👇 Ticket open/closed flag
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='open'
    )

    def __str__(self):
        return f"{self.subject} ({self.status})"


class ContactMessage(models.Model):
    thread = models.ForeignKey(
        ContactThread,
        related_name="messages",
        on_delete=models.CASCADE
    )
    sender = models.CharField(max_length=10)  # 'user' OR 'admin'
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.message[:30]}"
