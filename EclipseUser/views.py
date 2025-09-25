from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import CustomUserCreationForm, LoginForm, CustomUserChangeForm
from .models import CustomUser

def register_view(request):
    """
    Регистрация нового пользователя
    """
    if request.user.is_authenticated:
        return redirect('EclipseChat:main')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Автоматически входим после регистрации
            login(request, user)
            return redirect('EclipseUser:profile')
        else:
            return HttpResponse("Заполните регистрацию заново")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'EclipseUser/auth/register.html', {'form': form})

def login_view(request):
    """
    Вход пользователя
    """
    if request.user.is_authenticated:
        return redirect('EclipseUser:profile')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data['remember_me']
            
            # аутентифицировать по username
            user = authenticate(request, username=username, password=password)
            if user is None:
                messages.error(request, 'Неверное имя пользователя или пароль.')
            else:
                login(request, user)
                if not remember_me:
                    # сессия закончится при выходе из браузера
                    request.session.set_expiry(0)
                return redirect('EclipseUser:profile')
        else:
            return HttpResponse("Неверные данные")
    else:
        form = LoginForm()
    
    return render(request, 'EclipseUser/auth/login.html', {'form': form})

def logout_view(request):
    """
    Выход пользователя
    """
    logout(request)
    return redirect('EclipseUser:login')

@login_required
def profile_view(request):
    return render(request, 'EclipseUser/auth/profile.html')

@login_required
def profile_edit(request):
    """
    Просмотр и редактирование профиля
    """
    if request.method == 'POST': 
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('EclipseUser:profile')
        else:
            return HttpResponse("Данные введены некорректно")
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    return render(request, 'EclipseUser/auth/profile_edit.html', {'form': form})

@login_required
def delete_avatar(request):
    """
    Удаление аватарки пользователя
    """
    if request.method == 'POST':
        user = request.user
        if user.avatar:
            user.avatar.delete()
            user.avatar = None
            user.save()
            messages.success(request, 'Аватарка успешно удалена!')
        else:
            messages.info(request, 'Аватарка уже удалена.')
    
    return redirect('EclipseUser:profile')