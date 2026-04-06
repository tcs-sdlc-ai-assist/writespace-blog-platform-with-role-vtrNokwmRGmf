from django import forms
from django.contrib.auth.models import User


input_class = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': input_class,
            'placeholder': 'Enter your username',
        }),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': input_class,
            'placeholder': 'Enter your password',
        }),
    )

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise forms.ValidationError('Username is required.')
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        if not password:
            raise forms.ValidationError('Password is required.')
        return password


class RegistrationForm(forms.Form):
    display_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': input_class,
            'placeholder': 'Enter your display name',
        }),
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': input_class,
            'placeholder': 'Choose a username',
        }),
    )
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': input_class,
            'placeholder': 'Create a password (min 8 characters)',
        }),
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': input_class,
            'placeholder': 'Confirm your password',
        }),
    )

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise forms.ValidationError('Username is required.')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_display_name(self):
        display_name = self.cleaned_data.get('display_name', '').strip()
        if not display_name:
            raise forms.ValidationError('Display name is required.')
        return display_name

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data


ROLE_CHOICES = [
    ('user', 'User'),
    ('admin', 'Admin'),
]


class AdminCreateUserForm(forms.Form):
    display_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': input_class,
            'placeholder': 'Enter display name',
        }),
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': input_class,
            'placeholder': 'Enter username',
        }),
    )
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': input_class,
            'placeholder': 'Create a password (min 8 characters)',
        }),
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': input_class,
        }),
    )

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise forms.ValidationError('Username is required.')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_display_name(self):
        display_name = self.cleaned_data.get('display_name', '').strip()
        if not display_name:
            raise forms.ValidationError('Display name is required.')
        return display_name