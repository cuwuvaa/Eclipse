from django.urls import path
import EclipseServers.views as views

app_name = "EclipseServers"

urlpatterns = [
    path("<int:server_id>/", views.server, name="server"),
    path("create/", views.create, name="create"),
    path("", views.server_list_all, name="server_list_all"),
]
