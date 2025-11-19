from django.db import models
from django.utils import timezone
from EclipseRoom.models import room, roomuser

class RoomMessage(models.Model):
    room = models.ForeignKey(
        room.Room, 
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='комната'
    )
    
    room_user = models.ForeignKey(
        roomuser.RoomUser, 
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='отправитель'
    )

    text = models.TextField(verbose_name='Текст сообщения')

    timestamp = models.DateTimeField(
        default=timezone.now, 
        verbose_name='время отправки'
    )

    class Meta:
        verbose_name = 'сообщение'
        verbose_name_plural = 'сообщения'