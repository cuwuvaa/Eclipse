from rest_framework import generics, status, views
from rest_framework.views import APIView
from EclipseRoom.serializers.roomuser import RoomUserProfileSerializer, RoomSerializer, RoomUpdateSerializer
from EclipseRoom.serializers.roommessage import RoomMessageSerializer
from EclipseRoom.models.roomuser import RoomUser
from EclipseRoom.models.room import Room
from EclipseRoom.models.roommessage import RoomMessage
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from api.util.permissions import IsRoomMember, IsRoomAdminOrCreator, RoleChange, IsModerator, IsRoomCreator

class RoomDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsRoomCreator]
    queryset = Room.objects.all()
    lookup_url_kwarg = 'room_pk'

    def destroy(self, request, *args, **kwargs):
        room = self.get_object()
        passphrase = request.data.get('passphrase')
        if passphrase != f"delete {room.name}":
            return Response(
                {'error': 'Incorrect passphrase.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(room)
        return Response(status=status.HTTP_204_NO_CONTENT)

from rest_framework.permissions import IsAuthenticated
from api.util.pagination import MessagePagination

class RoomUpdateView(generics.UpdateAPIView):
    serializer_class = RoomUpdateSerializer
    permission_classes = [IsAuthenticated, IsRoomAdminOrCreator]
    queryset = Room.objects.all()
    lookup_url_kwarg = 'room_pk'

class RoomUsersAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsRoomMember]
    serializer_class = RoomUserProfileSerializer
    def get_queryset(self):
        room_pk = self.kwargs['room_pk']
        return RoomUser.objects.filter(room_id=room_pk)

class RoomsAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RoomSerializer
    queryset = Room.objects.all()

class RoomMessageAPI(generics.ListAPIView):
    serializer_class = RoomMessageSerializer
    permission_classes = [IsAuthenticated, IsRoomMember]
    pagination_class = MessagePagination
    
    def get_queryset(self):
        room_pk = self.kwargs['room_pk']
        return RoomMessage.objects.filter(room_id=room_pk).order_by('-timestamp')
    
class RoomMessageDeleteView(generics.DestroyAPIView):
    serializer_class = RoomMessageSerializer
    permission_classes = [IsAuthenticated, IsRoomAdminOrCreator]

    def get_object(self):
        obj = get_object_or_404(
            RoomMessage,
            pk=self.kwargs["message_pk"],
            room_id=self.kwargs["room_pk"]
        )
        self.check_object_permissions(self.request, obj)
        return obj
    
class RoomUserAPI(views.APIView):
    serializer_class = RoomUserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = get_object_or_404(
            RoomUser,
            pk=self.kwargs["roomuser_pk"],
            room_id=self.kwargs["room_pk"]
        )
        return obj

    def get(self, request, *args, **kwargs):
        room_user = self.get_object()
        serializer = self.serializer_class(room_user)
        return Response(serializer.data)

class RoomUserDeleteView(generics.DestroyAPIView):
    serializer_class = RoomMessageSerializer
    permission_classes = [IsAuthenticated, IsModerator]

    def get_object(self):
        obj = get_object_or_404(
            RoomUser,
            pk=self.kwargs["roomuser_pk"],
            room_id=self.kwargs["room_pk"]
        )

        self.check_object_permissions(self.request, obj)
        return obj

class RoomUserRoleUpdateView(APIView):
    permission_classes = [IsAuthenticated, RoleChange]

    def patch(self, request, room_pk, roomuser_pk):
        room_user = get_object_or_404(
            RoomUser, 
            pk=roomuser_pk, 
            room_id=room_pk
        )
        
        new_role = request.data.get('role')
        if new_role not in ['moderator', 'user']:
            return Response(
                {'error': 'Роль должна быть: moderator или user'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        if room_user.role == "creator":
            return Response(
                {'error': 'Нельзя понизить роль создателю'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        room_user.role = new_role
        room_user.save()
        
        return Response({'role': room_user.role})


class RoomBulkUsersAPI(APIView):
    """
    GET /api/rooms/<room_pk>/users/bulk/?user_ids=1,2,3
    """
    permission_classes = [IsAuthenticated, IsRoomMember]

    def get(self, request, *args, **kwargs):
        room_pk = self.kwargs['room_pk']
        
        user_ids_param = request.query_params.get('user_ids', '')
        if not user_ids_param:
            return Response(
                {"error": "Параметр 'user_ids' обязателен (например: ?user_ids=1,2,3)"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_ids = [int(uid.strip()) for uid in user_ids_param.split(',') if uid.strip()]
        except ValueError:
            return Response(
                {"error": "Некорректный формат user_ids. Ожидаются целые числа, разделённые запятыми."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user_ids:
            return Response(
                {"error": "Список user_ids пуст"},
                status=status.HTTP_400_BAD_REQUEST
            )

        room_users = RoomUser.objects.filter(
            room_id=room_pk,
            id__in=user_ids
        )

        # Сериализуем вручную
        serializer = RoomUserProfileSerializer(room_users, many=True)
        return Response(serializer.data)