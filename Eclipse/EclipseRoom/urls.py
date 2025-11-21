from django.urls import path
from EclipseRoom.views import Main, RoomCreate, RoomPage, RoomJoin

app_name = "rooms"

urlpatterns = [
    path("", Main.as_view(), name="main"),
    path("create/", RoomCreate.as_view(), name="create"),
    path("<int:room_pk>/", RoomPage.as_view(), name="room"),
    path("<int:room_pk>/join", RoomJoin.as_view(), name="room_join"),
]
