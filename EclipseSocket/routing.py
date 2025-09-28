from django.urls import path
from EclipseSocket import consumers


ws_urlpatterns = [
    path("ws/chat/<int:server_id>/", consumers.ChatConsumer.as_asgi()),
    path("ws/voicechat/<int:server_id>/", consumers.VoiceChatConsumer.as_asgi())
]