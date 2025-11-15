from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from EclipseUser.models.user import EclipseUser

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        label='username',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Как вас зовут?'
        })
    )
    password1 = forms.CharField(
        label='password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Придумайте пароль',
            'autocomplete': 'new-password'
        })
    )
    password2 = forms.CharField(
        label='password confirmation',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите пароль',
            'autocomplete': 'new-password'
        })
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if ' ' in username:
            raise ValidationError('имя пользователя не должно содержать пробелов')
        return username

    class Meta:
        model = EclipseUser
        fields = ['username','password1', 'password2']


class UserLoginForm(forms.Form):

    username = forms.CharField(
        label='username',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Как вас зовут?',
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш пароль',
            'autocomplete': 'current-password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Запомнить меня'
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:             #проверяем существование пользователя
            try:
                user = EclipseUser.objects.get(username=username)
            except EclipseUser.DoesNotExist:
                raise ValidationError('username не найден')

            if not user.check_password(password):
                raise ValidationError('неверный пароль')
            cleaned_data['user'] = user
        
        return cleaned_data