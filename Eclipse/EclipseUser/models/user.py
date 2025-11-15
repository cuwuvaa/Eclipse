import random
from django.db import models
from EclipseUser.models.usermanage import CustomUserManager
from EclipseUser.models.usermanage import AbstractBaseUser, PermissionsMixin
from django.utils import timezone

# Create your models here.
class EclipseUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('email',blank=True)
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
        
        if not self.avatar:
            default_avatars = [
                'avatars/defaults/account.png',
                'avatars/defaults/account(1).png',
                'avatars/defaults/account(2).png',
                'avatars/defaults/account(3).png',
                'avatars/defaults/account(4).png',
                'avatars/defaults/account(5).png',
            ]
            self.avatar = random.choice(default_avatars)

        super().save(*args, **kwargs)
