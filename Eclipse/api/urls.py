from django.urls import path
from api.views.room import RoomUsersAPI, RoomsAPI, RoomMessageAPI
from api.views.user import UserListAPI, UserDataAPI

app_name = "api"

urlpatterns = [
    path("room/<int:pk>/", RoomUsersAPI.as_view(), name="roomusers"),
    path("rooms/", RoomsAPI.as_view(), name="rooms"),
    path("messages/<int:pk>/", RoomMessageAPI.as_view(), name="roommessages"),
    path("users/", UserListAPI.as_view(),name="users" ),
    path("user/<int:pk>/", UserDataAPI.as_view(),name="user"),
]
