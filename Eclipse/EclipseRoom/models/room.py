from django.db import models
from django.utils import timezone

class Room(models.Model):
    name = models.CharField(
        'название',
        max_length=50)

    description = models.TextField(
        'описание',
        blank=True,
        null=True)

    created_at = models.DateTimeField(
        'дата создания',
        default=timezone.now
          )

    class Meta:
        verbose_name = 'комната'
        verbose_name_plural = 'комнаты'