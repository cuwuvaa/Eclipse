from rest_framework import serializers
from EclipseRoom.models.roommessage import RoomMessage
from api.serializers import UserAPISerializer

class RoomMessageSerializer(serializers.ModelSerializer):
    displayname = serializers.StringRelatedField(source='room_user.user.displayname')
    profilesender_id = serializers.IntegerField(source='room_user.user.id',read_only=True)
    roomsender_id = serializers.IntegerField(source='room_user.id', read_only=True)
    role = serializers.StringRelatedField(source='room_user.role')
    class Meta:
        model = RoomMessage
        fields = ("id","displayname", "roomsender_id", "profilesender_id", "role","text", "timestamp")
