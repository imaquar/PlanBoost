from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import Profile


class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(max_length=12,required=True, widget=forms.TextInput())

    class Meta:
        model = User
        fields = ['username']


class UpdateProfileForm(forms.ModelForm):
    avatar = forms.ImageField(widget=forms.FileInput())

    class Meta:
        model = Profile
        fields = ['avatar']

class RegisterForm(UserCreationForm):
    username = forms.CharField(max_length=12, widget=forms.TextInput(attrs={"placeholder": "username"}))
    password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={"placeholder": "password"}))
    password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={"placeholder": "confirm password"}))

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=12, required=True, 
                               widget=forms.TextInput(attrs={'placeholder': 'username'}))
    password = forms.CharField(max_length=50, required=True,
                               widget=forms.PasswordInput(attrs={'placeholder': 'password'}))
    remember_me = forms.BooleanField(required=False)