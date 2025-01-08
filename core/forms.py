from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from core.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'placeholder': 'Enter your username'
        })

        self.fields['email'].widget.attrs.update({
            'placeholder': 'Enter your email address'
        })

        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Enter your password'
        })

        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm your password'
        })



class loginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
            'class': 'username',
            'placeholder': 'Enter your username'
        }))
    password = forms.CharField(max_length=30, required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}))





