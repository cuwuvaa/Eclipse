from django.views import View
from django.shortcuts import render, redirect
from EclipseUser.models.user import EclipseUser

class Profile(View):
    def get(self,request, username):
        user = EclipseUser.objects.get(username=username)
        if username == request.user.username:
            return redirect("users:profile")
        return render(request, "user/profile.html", context={"USER":user})
    
class MyProfile(View):
    def get(self, request):
        return render(request, "user/profile.html", context={"USER": request.user})

    def post(self, request):
        displayname = request.POST.get('displayname')
        avatar = request.FILES.get('avatar')
        user = request.user
        if displayname:
            user.displayname = displayname
        if avatar:
            user.avatar = avatar
        user.save()
        return redirect("users:profile")