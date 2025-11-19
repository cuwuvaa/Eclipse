from rest_framework import serializers
from EclipseRoom.models.roomuser import RoomUser
from EclipseRoom.models.room import Room

class RoomUserProfileSerializer(serializers.ModelSerializer):
    displayname = serializers.StringRelatedField(source='user')
    role = serializers.ChoiceField(choices=RoomUser.ROLE_CHOICES) # Make role writable
    
    class Meta:
        model = RoomUser
        fields = "__all__"


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"
