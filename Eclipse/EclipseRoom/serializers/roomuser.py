from rest_framework import serializers
from EclipseRoom.models.roomuser import RoomUser
from EclipseRoom.models.room import Room
from EclipseUser.util.redis import is_user_online

class RoomUserProfileSerializer(serializers.ModelSerializer):
    displayname = serializers.StringRelatedField(source='user.displayname')
    is_online = serializers.SerializerMethodField() 
    role = serializers.ChoiceField(choices=RoomUser.ROLE_CHOICES)
    
    class Meta:
        model = RoomUser
        fields = "__all__"

    def get_is_online(self, obj):
        return is_user_online(obj.user.id)

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"
