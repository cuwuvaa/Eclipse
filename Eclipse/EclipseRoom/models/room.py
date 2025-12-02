from django.db import models
from django.utils import timezone

class Room(models.Model):
    name = models.CharField(
        'name',
        max_length=50)

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