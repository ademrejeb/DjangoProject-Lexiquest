# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email','image','cv_file']  # Include fields you want to update


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        )
    )



class SignUpForm(UserCreationForm):
    fullname = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Full Name",
                "class": "form-control"
            }
        ))
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "User Name",
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    cin = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "CIN",
                "class": "form-control"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm Password",
                "class": "form-control"
            }
        ))

    class Meta:
        model = CustomUser
        fields = ('fullname', 'username', 'email', 'cin', 'password1', 'password2')
