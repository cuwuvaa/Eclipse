from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import VoiceServer, ServerMember
from .forms import VoiceServerCreateForm, VoiceServerEditForm

# Create your views here.
@login_required
def create(request):
    """Создание нового сервера"""
    if request.method == 'POST':
        form = VoiceServerCreateForm(request.POST)
        if form.is_valid():
            server = form.save(commit=False)
            server.owner = request.user
            server.save()
            
            # Добавляем владельца как участника сервера с ролью owner
            ServerMember.objects.create(
                user=request.user,
                server=server,
                role='owner'
            )
            
            messages.success(request, f'Сервер "{server.name}" успешно создан!')
            return redirect(reverse("EclipseServers:server", args=[server.id]))
    else:
        form = VoiceServerCreateForm()
    
    return render(request, 'EclipseServers/createserver.html', {'form': form})

@login_required
def server(request,server_id):
    server = VoiceServer.objects.all().get(id=server_id)
    if request.method == "POST":
        new_member = ServerMember(user=request.user, server=server)
        new_member.save()
        
    return render(request, "EclipseServers/server.html", {"server":server})

@login_required
def server_list_all(request):
    servers = VoiceServer.objects.all()
    return render(request, "EclipseServers/serverbrowse.html", {
        "servers":servers
    })