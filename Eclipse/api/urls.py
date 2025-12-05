from django.urls import path
from api.views.room import RoomUsersAPI, RoomsAPI, RoomMessageAPI, RoomUserAPI, RoomUpdateView, RoomDeleteView
from api.views.user import UserListAPI, UserDataAPI
from api.views.room import RoomMessageDeleteView, RoomUserDeleteView, RoomUserRoleUpdateView, RoomBulkUsersAPI

app_name = "api"

urlpatterns = [
    path("rooms/", RoomsAPI.as_view(), name="rooms"),
    path("rooms/<int:room_pk>/update/", RoomUpdateView.as_view(), name="roomupdate"),
    path("rooms/<int:room_pk>/delete/", RoomDeleteView.as_view(), name="roomdelete"),
    path("rooms/<int:room_pk>/users/", RoomUsersAPI.as_view(), name="roomusers"),
    path('rooms/<int:room_pk>/users/<int:roomuser_pk>/', RoomUserAPI.as_view(), name='roomuser'),
    path('rooms/<int:room_pk>/users/<int:roomuser_pk>/delete/', RoomUserDeleteView.as_view(), name='roomuserdelete'),
    path('rooms/<int:room_pk>/users/<int:roomuser_pk>/role/', RoomUserRoleUpdateView.as_view(), name='roomuserrole'),
    path("rooms/<int:room_pk>/messages/", RoomMessageAPI.as_view(), name="roommessages"),
    path('rooms/<int:room_pk>/messages/<int:message_pk>/delete/', RoomMessageDeleteView.as_view(), name='messagedelete'),
    path('rooms/<int:room_pk>/users/bulk/', RoomBulkUsersAPI.as_view(), name="roomuserbulk"),
    path("users/", UserListAPI.as_view(),name="users" ),
    path("users/<int:pk>/", UserDataAPI.as_view(),name="user"),
]
