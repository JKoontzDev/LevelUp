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
            'placeholder': 'Enter your password',
            'class': 'passwordView'
        })

        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm your password',
            'class': 'passwordView'
        })



class loginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
            'class': 'username',
            'placeholder': 'Enter your username'
        }))
    password = forms.CharField(max_length=30, required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password',
                                                                                               'class': 'passwordView'}))


class settingsForm(forms.Form):
    number_of_quests = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Enter your goal'}))
    profile_pic = forms.ImageField(required=False)
    problem_report = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Please describe the bug in detail, including steps to reproduce it.'}),
        max_length=1000,
        required=False,
        label='Describe the bug',
        help_text='Include steps to reproduce the issue.'
    )



