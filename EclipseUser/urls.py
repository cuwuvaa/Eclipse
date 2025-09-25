from django.urls import path
import EclipseUser.views as views

app_name = "EclipseUser"

urlpatterns = [
    path('', views.profile_view, name='profile'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('edit/', views.profile_edit, name='profile_edit'),
    path('delete-avatar/', views.delete_avatar, name='delete_avatar'),
]
