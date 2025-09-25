from django.urls import path
import EclipseChat.views

app_name = "EclipseChat"

urlpatterns = [
    path("main/", EclipseChat.views.index, name="main")
]
