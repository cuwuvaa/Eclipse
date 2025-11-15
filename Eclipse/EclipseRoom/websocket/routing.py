from django.urls import path
from EclipseRoom.websocket import consumers


ws_urlpatterns = [
    path("ws/<int:room_id>/", consumers.ChatConsumer.as_asgi())
]