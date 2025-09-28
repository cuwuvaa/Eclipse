from django.contrib import admin
import EclipseServers.models as Server
# Register your models here.

admin.site.register(Server.Server)
admin.site.register(Server.ServerMessage)