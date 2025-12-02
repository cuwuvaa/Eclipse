from django.views import View
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import login, logout

from django.http import HttpResponse

from EclipseUser.forms.auth import UserRegisterForm, UserLoginForm


class RegisterView(View):

    def get(self, request):
        form = UserRegisterForm #registration form
        context = {
            'form': form,
            'title': 'Registration'
        }
        return render(request, "auth/register.html", context)
    
    def post(self, request):
        form = UserRegisterForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('rooms:main')
        else:
            context = {
                'form': form,
                'title': 'Registration'
            }
            return render(request, "auth/register.html", context)
    

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs): #if user is already logged in, redirect
        if request.user.is_authenticated:
            return redirect('rooms:main')
        return super().dispatch(request, *args, **kwargs)
    
class LoginView(View):

    def get(self, request):
        form = UserLoginForm #authorization form
        context = {
            'form': form,
            'title': 'Login'
        }
        return render(request, "auth/login.html", context)

    def post(self, request):
        form = UserLoginForm(request.POST)
        
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            return redirect('rooms:main')
        else:
            context = {
                'form': form,
                'title': 'Login'
            }
            return render(request, "auth/login.html", context)

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs): #if user is already logged in, redirect
        if request.user.is_authenticated:
            return redirect('rooms:main')
        return super().dispatch(request, *args, **kwargs)
    
class LogoutView(View):

    def get(self,request):
        logout(request)
        return render(request, "auth/logout.html")