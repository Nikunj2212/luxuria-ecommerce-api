from django.contrib import admin
from .models import User, Address

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone', 'username', 'is_staff', 'profile_completed')
    search_fields = ('email', 'phone')
    list_filter = ('is_staff', 'profile_completed')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'state', 'pincode')
