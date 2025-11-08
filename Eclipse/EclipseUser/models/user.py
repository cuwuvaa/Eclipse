from django.db import models
from EclipseUser.models.usermanage import CustomUserManager
from EclipseUser.models.usermanage import AbstractBaseUser, PermissionsMixin
from django.utils import timezone

# Create your models here.
class EclipseUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('email', unique=True)
    username = models.CharField('username', unique=True, max_length=50, blank=True)
    displayname = models.CharField('displayname', max_length=50, blank=True)
    avatar = models.ImageField('аватар', upload_to='avatars/', null=True, blank=True)
    
    is_staff = models.BooleanField('статус персонала', default=False)
    date_joined = models.DateTimeField('дата регистрации', default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = [] #для su

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def save(self, *args, **kwargs):
        if not self.displayname:
            self.displayname = self.username
        super().save(*args, **kwargs)
