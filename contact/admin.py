from django.contrib import admin
from .models import ContactThread, ContactMessage

admin.site.register(ContactThread)
admin.site.register(ContactMessage)
