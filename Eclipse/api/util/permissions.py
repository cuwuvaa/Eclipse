from rest_framework.permissions import BasePermission
from EclipseRoom.models.roomuser import RoomUser
from EclipseRoom.models.room import Room
from EclipseRoom.models.roommessage import RoomMessage

class IsRoomAdminOrCreator(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if isinstance(obj, RoomMessage):
            room = obj.room
            if obj.room_user.user == user:
                return True
        elif isinstance(obj, Room):
            room = obj
        else:
            return False

        try:
            room_user = RoomUser.objects.get(room=room, user=user)
        except RoomUser.DoesNotExist:
            return False

        return room_user.role in [RoomUser.ROLE_CREATOR, RoomUser.ROLE_MODERATOR]

class IsRoomCreator(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        try:
            room_user = RoomUser.objects.get(room=obj, user=user)
        except RoomUser.DoesNotExist:
            return False
        return room_user.role == RoomUser.ROLE_CREATOR



class IsModerator(BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            room_user = RoomUser.objects.get(room=obj.room, user=request.user)
        except RoomUser.DoesNotExist:
            return False

        return (room_user.role in [RoomUser.ROLE_CREATOR, RoomUser.ROLE_MODERATOR] and obj.role != "creator")
    
class RoleChange(BasePermission):
    def has_object_permission(self, request, view, obj):
        user_to_be_changed = obj # This is the RoomUser instance whose role is being changed
        room = user_to_be_changed.room
        user = request.user # This is the user making the PATCH request

        try:
            # Get the RoomUser profile of the user making the request
            user_making_request_profile = RoomUser.objects.get(room=room, user=user)
        except RoomUser.DoesNotExist:
            return False

        return user_making_request_profile.role in [RoomUser.ROLE_CREATOR, RoomUser.ROLE_MODERATOR] and  (user_making_request_profile != user_to_be_changed) and user_to_be_changed.role != RoomUser.ROLE_CREATOR

class IsRoomMember(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        room_id = view.kwargs.get('room_pk')
        if room_id:
            return request.user.room_users.filter(room_id=room_id).exists()
        return False