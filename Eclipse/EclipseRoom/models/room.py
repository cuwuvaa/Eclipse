import random
from django.db import models
from django.utils import timezone

class Room(models.Model):
    name = models.CharField(
        'name',
        max_length=50)
    
    avatar = models.ImageField(
        'аватар',
        upload_to='rooms/',
        null=True,
        blank=True)

    description = models.TextField(
        'description',
        blank=True,
        null=True)

    created_at = models.DateTimeField(
        'creation date',
        default=timezone.now
          )

    class Meta:
        verbose_name = 'room'
        verbose_name_plural = 'rooms'

    def save(self, *args, **kwargs):
        if not self.avatar:
            default_avatars = [
                'rooms/defaults/room.png',
                'rooms/defaults/room(1).png',
                'rooms/defaults/room(2).png',
                'rooms/defaults/room(3).png',
            ]
            self.avatar = random.choice(default_avatars)

        super().save(*args, **kwargs)