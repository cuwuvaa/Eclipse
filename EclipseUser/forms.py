from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.core.exceptions import ValidationError
import re

class CustomUserCreationForm(UserCreationForm):
    """
    Форма для создания нового пользователя
    """

    username = forms.CharField(
        label="Никнейм",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите пароль',
        })
    )

    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        }),
        help_text="Пароль должен содержать не менее 8 символов, включая буквы и цифры."
    )
    
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите пароль'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя пользователя'
            }),
        }
    
    def clean_username(self):
        """Валидация имени пользователя"""
        username = self.cleaned_data['username']
        
        # Проверяем длину
        if len(username) < 3 or len(username) >= 50:
            raise ValidationError("Имя пользователя должно содержать не менее 3 символов и не более 50.")
        
        # Проверяем допустимые символы
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("Имя пользователя может содержать только буквы, цифры и подчеркивания.")
        
        return username
    
    def clean_password1(self):
        """Валидация пароля"""
        password1 = self.cleaned_data.get('password1')
        
        if len(password1) < 8:
            raise ValidationError("Пароль должен содержать не менее 8 символов.")
        
        if not re.search(r'[A-Za-z]', password1) or not re.search(r'[0-9]', password1):
            raise ValidationError("Пароль должен содержать как буквы, так и цифры.")
        
        return password1
    
    def clean(self):
        """Общая валидация формы"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароли не совпадают.")
        
        return cleaned_data

class CustomUserChangeForm(UserChangeForm):
    """
    Форма для редактирования профиля пользователя
    """
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'avatar', 'bio')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class LoginForm(forms.Form):
    """
    Форма для входа пользователя
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Никнейм'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )