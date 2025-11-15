from rest_framework import permissions

class IsRoomMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        room_id = view.kwargs.get('pk')
        if room_id:
            return request.user.room_users.filter(room_id=room_id).exists()
        return False