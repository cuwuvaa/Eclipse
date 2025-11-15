from django.urls import path
from EclipseRoom.views import Main, RoomCreate, RoomPage

app_name = "rooms"

urlpatterns = [
    path("", Main.as_view(), name="main"),
    path("create/", RoomCreate.as_view(), name="create"),
    path("<int:pk>/", RoomPage.as_view(), name="room"),
]
