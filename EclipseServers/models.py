from django.db import models
from EclipseUser.models import CustomUser as User


class ServerManager(models.Manager):
    def current_user(self, user):
        return self.filter(user=user)
        
#todo: сделать закрытые серверы
class Server(models.Model):
    """
    Сервер - аналогично Discord серверу
    """
    name = models.CharField(max_length=100, verbose_name="Название сервера")
    image = models.ImageField(default="default_images/default_server.png")
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="Владелец",
        related_name='owned_servers'
    )
    members = models.ManyToManyField(
        User, 
        through='ServerMember',
        related_name='servers'
    )
    bio = models.CharField(max_length=500, verbose_name="О сервере")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
    user_objects = ServerManager()
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Голосовой сервер"
        verbose_name_plural = "Голосовые серверы"

class ServerMember(models.Model):
    """
    Члены сервера с ролями
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    ROLE_CHOICES = [ #todo: добавить функционал для этих ролей
        ('owner', 'Владелец'),
        ('admin', 'Администратор'),
        ('member', 'Участник'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'server')

class ServerMessage(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    sender = models.ForeignKey(ServerMember, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']