from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from EclipseUser.models.user import EclipseUser

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        label='username',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Choose a username'
        })
    )
    password1 = forms.CharField(
        label='password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter a password',
            'autocomplete': 'new-password'
        })
    )
    password2 = forms.CharField(
        label='password confirmation',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password'
        })
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if ' ' in username:
            raise ValidationError('Username should not contain spaces')
        return username

    class Meta:
        model = EclipseUser
        fields = ['username','password1', 'password2']


class UserLoginForm(forms.Form):

    username = forms.CharField(
        label='username',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your username',
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:             #check if user exists
            try:
                user = EclipseUser.objects.get(username=username)
            except EclipseUser.DoesNotExist:
                raise ValidationError('User not found')

            if not user.check_password(password):
                raise ValidationError('Incorrect password')
            cleaned_data['user'] = user
        
        return cleaned_data