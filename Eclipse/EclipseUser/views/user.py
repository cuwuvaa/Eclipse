from django.views import View
from django.shortcuts import render, redirect
from EclipseUser.models.user import EclipseUser

class Profile(View):
    def get(self,request, username):
        user = EclipseUser.objects.get(username=username)
        if username == request.user.username:
            return redirect("user:profile")
        return render(request, "user/profile.html", context={"USER":user})
    
class MyProfile(View):
    def get(self, request):
        return render(request, "user/profile.html", context={"USER":request.user})