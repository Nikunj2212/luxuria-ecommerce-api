from django import forms
from .models import User, Address
from django.contrib.auth import authenticate

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'phone', 'password']

class LoginForm(forms.Form):
    email_or_phone = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['house_no','address_line1','landmark','area','city','state','pincode']


class AdminCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'phone', 'username', 'password']