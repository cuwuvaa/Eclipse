from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views import View
from EclipseRoom.forms.create import RoomCreationForm
from EclipseRoom.models.room import Room
from EclipseRoom.models.roomuser import RoomUser
# Create your views here.

class Main(View):
    def get(self, request):
        query = request.GET.get('q')
        if query:
            rooms = Room.objects.filter(name__icontains=query)
        else:
            rooms = Room.objects.all()
        return render(request, "main/main.html", context={"rooms": rooms, "query": query})
    
class RoomCreate(LoginRequiredMixin, View):
    
    def get(self, request):
        form = RoomCreationForm
        return render(request, "room/create.html", context={"form":form})
    
    def post(self,request):
        form = RoomCreationForm(request.POST, request.FILES)
        
        if form.is_valid():
            room = form.save()
            RoomUser.objects.create(
                user=request.user, 
                room=room, 
                role=RoomUser.ROLE_CREATOR
            )
            return redirect("rooms:room", room_pk=room.id)
        
class RoomPage(LoginRequiredMixin, View):
    
    def get(self, request, room_pk):
        room = Room.objects.get(id=room_pk)
        participants = RoomUser.objects.filter(room=room)
        is_participant = participants.filter(user=request.user).exists()
        if (is_participant):
            return render(request, "room/room.html", context={
                "room": room,
                "is_participant": is_participant
            })
        else:
            return redirect("rooms:room_join", room_pk=room_pk)
        
class RoomJoin(LoginRequiredMixin, View):
    def get(self, request, room_pk):
        room = Room.objects.get(id=room_pk)
        return render(request, "room/enter.html", context={"room":room})

    def post(self,request, room_pk):
        new_user = RoomUser(room_id=room_pk, user=request.user)
        new_user.save()
        return redirect("rooms:room", room_pk=room_pk)

class MyRooms(LoginRequiredMixin, View):
    def get(self, request):
        user_rooms = RoomUser.objects.filter(user=request.user)
        rooms = [user_room.room for user_room in user_rooms]
        return render(request, "room/my_rooms.html", context={"rooms": rooms})
