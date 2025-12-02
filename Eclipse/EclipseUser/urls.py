from django.urls import path
from EclipseUser.views import auth, user


app_name = "users"

urlpatterns = [
    path("register/", auth.RegisterView.as_view(), name="register"),
    path("login/", auth.LoginView.as_view(), name="login"),
    path("logout/", auth.LogoutView.as_view(), name="logout"),
    path("profiles/<str:username>/", user.Profile.as_view(), name="profiles"),
    path("profile/", user.MyProfile.as_view(), name="profile"),
]
