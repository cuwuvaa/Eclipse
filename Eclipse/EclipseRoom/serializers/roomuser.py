from rest_framework import serializers
from EclipseRoom.models.roomuser import RoomUser
from EclipseRoom.models.room import Room

class RoomUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomUser
        fields = "__all__"


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"
