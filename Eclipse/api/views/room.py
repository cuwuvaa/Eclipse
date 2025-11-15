from rest_framework import generics, status
from EclipseRoom.serializers.roomuser import RoomUserProfileSerializer, RoomSerializer
from EclipseRoom.serializers.roommessage import RoomMessageSerializer
from EclipseRoom.models.roomuser import RoomUser
from EclipseRoom.models.room import Room
from EclipseRoom.models.roommessage import RoomMessage
from rest_framework.response import Response

from api.util.permissions import IsRoomMember
from rest_framework.permissions import IsAuthenticated

class RoomUsersAPI(generics.ListAPIView):
    serializer_class = RoomUserProfileSerializer
    def get_queryset(self):
        room_pk = self.kwargs['pk']
        return RoomUser.objects.filter(room_id=room_pk)

class RoomsAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RoomSerializer
    queryset = Room.objects.all()

class RoomMessageAPI(generics.ListAPIView):
    serializer_class = RoomMessageSerializer
    permission_classes = [IsAuthenticated, IsRoomMember]
    
    def get_queryset(self):
        room_pk = self.kwargs['pk']
        return RoomMessage.objects.filter(room_id=room_pk)



