from django.db import models
from django.utils import timezone
from EclipseRoom.models import room
from EclipseUser.models import user

class RoomUser(models.Model):
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
    
    signup_date = models.DateTimeField(
        default=timezone.now, 
        verbose_name='дата присоединения к комнате'
    )

    class Meta:
        verbose_name = 'участник комнаты'
        verbose_name_plural = 'участники комнат'