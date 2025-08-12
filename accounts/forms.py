from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label="User Name", 
        help_text="Maximum length is 150 characters. Can contain letters, numbers, and @/./+/-/_.",
    )
    email = forms.EmailField(
        label="Email",
        help_text="Please enter a valid email address.",
        error_messages={
            'invalid': "Please enter a valid email address."
        }
    )

    first_name = forms.CharField(
    label="First Name",
    max_length=30,
    required=False,
    help_text="Optional. Maximum length is 30 characters.",
    )

    last_name = forms.CharField(
        label="Last Name",
        max_length=30,
        required=False,
        help_text="Optional. Maximum length is 30 characters.",
    )

    password1 = forms.CharField(
        label="Password",
        help_text="Must be at least 8 characters, cannot be a common password, and cannot be entirely numbers.",
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="Confirm Password",
        help_text="Please enter your password again to confirm.",
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")