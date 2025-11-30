from django.urls import path
from EclipseRoom.websocket import redis


ws_urlpatterns = [
    path("ws/<int:room_id>/", redis.ChatConsumer.as_asgi())
]