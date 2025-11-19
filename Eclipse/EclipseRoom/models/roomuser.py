from django.db import models
from django.utils import timezone
from EclipseRoom.models import room
from EclipseUser.models import user

class RoomUser(models.Model):
    ROLE_CREATOR = 'creator'
    ROLE_MODERATOR = 'moderator'
    ROLE_USER = 'user'
    
    ROLE_CHOICES = [
        (ROLE_CREATOR, 'cоздатель'),
        (ROLE_MODERATOR, 'модератор'),
        (ROLE_USER, 'пользователь'),
    ]

    room = models.ForeignKey(
        room.Room, 
        on_delete=models.CASCADE,
        related_name='room_users'
    )
    user = models.ForeignKey(
        user.EclipseUser, 
        on_delete=models.CASCADE,
        related_name='room_users'
    )
    
    role = models.CharField(
        'роль',
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_USER
    )

    is_banned = models.BooleanField(
        'забанен', 
        default=False
    )
    
    signup_date = models.DateTimeField(
        default=timezone.now, 
        verbose_name='дата присоединения к комнате'
    )

    class Meta:
        verbose_name = 'участник комнаты'
        verbose_name_plural = 'участники комнат'
        unique_together = ('room', 'user') # Add this line
