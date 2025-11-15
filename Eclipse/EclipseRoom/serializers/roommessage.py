from rest_framework import serializers
from EclipseRoom.models.roommessage import RoomMessage
from api.serializers import UserAPISerializer

class RoomMessageSerializer(serializers.ModelSerializer):
    displayname = serializers.StringRelatedField(source='room_user')
    class Meta:
        model = RoomMessage
        fields = ("displayname", "text", "timestamp")
