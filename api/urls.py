from django.urls import path
import api.views as views

app_name = "api"

urlpatterns = [
    path("user/<int:userid>/", views.get_user_data, name="get_user")
]
