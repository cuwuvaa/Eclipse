from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views import View
from EclipseRoom.forms.create import RoomCreationForm
from EclipseRoom.models.room import Room
from EclipseRoom.models.roomuser import RoomUser
# Create your views here.

class Main(View):

    def get(self,request):
        rooms = Room.objects.all()
        return render(request, "main/main.html", context={"rooms":rooms})
    
class RoomCreate(LoginRequiredMixin, View):
    
    def get(self, request):
        form = RoomCreationForm
        return render(request, "room/create.html", context={"form":form})
    
    def post(self,request):
        form = RoomCreationForm(request.POST)
        
        if form.is_valid():
            room = form.save()
            RoomUser.objects.create(
                user=request.user, 
                room=room, 
                role=RoomUser.ROLE_CREATOR
            )
            return redirect("rooms:room", pk=room.id)
        
class RoomPage(LoginRequiredMixin, View):
    
    def get(self, request, pk):
        room = Room.objects.get(id=pk)
        participants = RoomUser.objects.filter(room=room)
        is_participant = participants.filter(user=request.user).exists()
        return render(request, "room/room.html", context={
            "room": room,
            "participants": participants,
            "is_participant": is_participant
        })
    
    def post(self, request, pk):
        if 'join' in request.POST:
            RoomUser.objects.get_or_create(user=request.user, room_id=pk)
            return redirect("rooms:room", pk=pk)
