from django.urls import path
from EclipseSocket import consumers


ws_urlpatterns = [
    path("ws/server/<int:server_id>/", consumers.ChatConsumer.as_asgi())
]