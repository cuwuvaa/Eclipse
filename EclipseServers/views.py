from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Server, ServerMember, ServerMessage
from .forms import ServerCreateForm, ServerEditForm

# Create your views here.
@login_required
def create(request):
    """Создание нового сервера"""
    if request.method == 'POST':
        form = ServerCreateForm(request.POST)
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
            
            return redirect(reverse("EclipseServers:server", args=[server.id]))
    else:
        form = ServerCreateForm()
    
    return render(request, 'EclipseServers/createserver.html', {'form': form})

@login_required
def server(request,server_id):
    server = Server.objects.all().get(id=server_id)
    server_messages = ServerMessage.objects.all().filter(server=server)
    if request.method == "POST":
        new_member = ServerMember(user=request.user, server=server)
        new_member.save()
        
    return render(request, "EclipseServers/server.html", {"server":server, "server_messages":server_messages})

@login_required
def server_list_all(request):
    servers = Server.objects.all()
    return render(request, "EclipseServers/serverbrowse.html", {
        "servers":servers
    })