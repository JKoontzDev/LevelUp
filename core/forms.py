from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from core.models import CustomUser, enemies


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    privacy_check = forms.BooleanField(
        label="I agree to the Privacy Policy",
        required=True,
        error_messages={'required': 'You must agree to the Privacy Policy to register.'}
    )

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


class RedeemEmailForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter email used with Buy Me a Coffee to redeem',
            'class': 'form-control'
        }),
        required=True
    )


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
    user_avatar = forms.ImageField(required=False)
    problem_report = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Please describe the bug in detail, including steps to reproduce it.'}),
        max_length=1000,
        required=False,
        label='Describe the bug',
        help_text='Include steps to reproduce the issue.'
    )
    improvements = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 2, 'placeholder': 'Please describe improvements here'}),
        max_length=500,
        required=False,
        label='Improvements',
    )



class taskForm(forms.Form):
    TASK_FREQUENCY_CHOICES = [
        ('everyday', 'Everyday'),
        ('random', 'Random'),
    ]
    title = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter your task title'}))
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Please describe this task'}),
        max_length=400,
        required=True,
        label='Describe this task',
        help_text='Describe this task'
    )
    frequency = forms.ChoiceField(
        label='Frequency',
        choices=TASK_FREQUENCY_CHOICES,
        widget=forms.RadioSelect,
        initial='everyday'
    )


class SceneForm(forms.Form):
    scene_id = forms.CharField(max_length=100, label="Scene ID")
    character = forms.CharField(widget=forms.Textarea, label="Character Name")
    character_url = forms.CharField(widget=forms.Textarea, label="Character Url")
    dialogue = forms.CharField(widget=forms.Textarea, label="Dialogue")
    enemies = forms.CharField(
        required=False,
        widget=forms.Textarea,
        label="Enemies (one per line)",
        help_text="Enter enemy names exactly as stored in the Enemy model."
    )


class ChoiceForm(forms.Form):
    text = forms.CharField(label="Choice Text")
    next_scene = forms.CharField(label="Next Scene ID")
    stats_requirement = forms.CharField(
        required=False,
        label="Stats Requirement (e.g. strength:5)",
        help_text="Format: stat:amount (e.g. strength:5)"
    )
    inventory_requirement = forms.CharField(
        required=False,
        label="Inventory Requirement (comma-separated)",
        help_text="e.g. gold_coin,sword"
    )
    reward = forms.CharField(
        required=False,
        label="Reward (comma-separated)",
        help_text="e.g. gold_coin,item"
    )