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
    fname = forms.CharField(label="Enter first name :", max_length=50, required=True, 
                          error_messages={'required': 'First name is required'})
    lname = forms.CharField(label="Enter last name :", max_length=50, required=True,
                          error_messages={'required': 'Last name is required'})
    email = forms.EmailField(label="Enter the email", required=True,
                           error_messages={
                               'required': 'Email address is required',
                               'invalid': 'Please enter a valid email address'
                           })
    password = forms.CharField(label="Enter the password", min_length=6, max_length=20, 
                             required=True, widget=forms.PasswordInput,
                             error_messages={
                                 'required': 'Password is required',
                                 'min_length': 'Password must be at least 6 characters long'
                             })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError('Email address is required')
        
        # Check email format
        if '@' not in email or '.' not in email:
            raise ValidationError('Please enter a valid email address')
            
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise ValidationError('An account with this email already exists')
            
        return email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise ValidationError('Password is required')
            
        # Check password length
        if len(password) < 6:
            raise ValidationError('Password must be at least 6 characters long')
            
        return make_password(password)


class TaskScreenshotForm(forms.Form):
    image = forms.ImageField(label=(""), required=True)