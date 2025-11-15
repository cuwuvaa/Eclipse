from django.views import View
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import login, logout

from django.http import HttpResponse

from EclipseUser.forms.auth import UserRegisterForm, UserLoginForm


class RegisterView(View):

    def get(self, request):
        form = UserRegisterForm #форма регистрации
        context = {
            'form': form,
            'title': 'Регистрация'
        }
        return render(request, "auth/register.html", context)
    
    def post(self, request):
        form = UserRegisterForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('user:profile', username=user.username)
        else:
            return HttpResponse("error while register")
    

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs): #если пользователь уже авторизован, перенаправляем
        if request.user.is_authenticated:
            return HttpResponse(f"you are logged in already as {request.user.username}")
        return super().dispatch(request, *args, **kwargs)
    
class LoginView(View):

    def get(self, request):
        form = UserLoginForm #форма авторизации
        context = {
            'form': form,
            'title': 'Авторизация'
        }
        return render(request, "auth/login.html", context)

    def post(self, request):
        form = UserLoginForm(request.POST)
        
        if form.is_valid():
            user = form.cleaned_data['user']
            remember = form.cleaned_data.get("remember_me", False)
            login(request, user)
            
            if remember:
                request.session.set_expiry(60 * 60 * 24 * 14) #14 дней
            else:
                request.session.set_expiry(0) #по закрытии браузера

            return HttpResponse("you are logged in!")
        else:
            return HttpResponse("error while logging in")

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs): #если пользователь уже авторизован, перенаправляем
        if request.user.is_authenticated:
            return HttpResponse(f"you are logged in already as {request.user.username}")
        return super().dispatch(request, *args, **kwargs)
    
class LogoutView(View):

    def get(self,request):
        logout(request)
        return redirect("user:login")