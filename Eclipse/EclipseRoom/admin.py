from django.contrib import admin
from EclipseRoom.models import room, roommessage, roomuser
# Register your models here.

admin.site.register(room.Room)
admin.site.register(roommessage.RoomMessage)
admin.site.register(roomuser.RoomUser)