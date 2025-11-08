from django.urls import path
from EclipseUser.api import api


app_name = "user"

urlpatterns = [
    path("api/", api.UserListAPI.as_view()),
    path("api/createuser", api.UserRegisterAPI.as_view()),
]
