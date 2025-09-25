from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
import os
from uuid import uuid4

def avatar_upload_path(instance, filename):
    """Генерируем путь для загрузки аватарки"""
    ext = filename.split('.')[-1]
    filename = f"{uuid4()}.{ext}"
    return os.path.join('avatars', str(instance.id), filename)

class CustomUser(AbstractUser):
    """
    Кастомная модель пользователя 
    """
    # Дополнительные поля
    email = models.EmailField(
        verbose_name='Email адрес',
        unique=True,  # Email должен быть уникальным
        error_messages={
            'unique': "Пользователь с таким email уже существует.",
        }
    )
    
    avatar = models.ImageField(
        verbose_name='Аватарка',
        upload_to=avatar_upload_path,
        blank=True,
        null=True,
        default='/default_images/default_avatar.png'
    )
    
    bio = models.TextField(
        verbose_name='О себе',
        max_length=500,
        blank=True,
        null=True
    )
    
    # Статус онлайн/офлайн
    is_online = models.BooleanField(
        verbose_name='Онлайн',
        default=False
    )
    
    # Последняя активность
    last_activity = models.DateTimeField(
        verbose_name='Последняя активность',
        auto_now=True
    )
    
    # Подтверждение email
    email_verified = models.BooleanField(
        verbose_name='Email подтвержден',
        default=False
    )
    
    def __str__(self):
        return self.username
    
    def get_avatar_url(self):
        """Возвращает URL аватарки или дефолтную"""
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return '/static/images/default_avatar.png'
    
    def get_display_name(self):
        """Возвращает отображаемое имя (username)"""
        return self.username
    
    @property
    def is_verified(self):
        """Проверяет, подтвержден ли email"""
        return self.email_verified
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        db_table = 'custom_user'