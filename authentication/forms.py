from django import forms 
from django.core.exceptions import ValidationError
from .models import User
from django.contrib.auth.hashers import make_password, check_password

class UserLoginForm(forms.Form):
    email = forms.CharField(label="enter your Email ",max_length=100)
    password = forms.CharField(label="enter your password ",widget=forms.PasswordInput)

class UserLogoutForm(forms.Form):
    pass

class UserSignupForm(forms.Form):
    def clean(self):
        cleaned_data = super().clean()
        email_to_check = cleaned_data.get('email')
        if User.objects.filter(email=email_to_check).exists():
            raise ValidationError('Email already exists')

    fname = forms.CharField(label="Enter first name :",max_length=50, required=True)
    lname = forms.CharField(label="Enter last name :", max_length=50,required=True)
    email = forms.EmailField(label="Enter the email", required=True)
    password = forms.CharField(label="Enter the password",max_length=8, widget=forms.PasswordInput)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        return make_password(password)


class TaskScreenshotForm(forms.Form):
    image = forms.ImageField(label=(""), required=True)