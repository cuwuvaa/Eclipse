from rest_framework import serializers
from .models import ServerMessage, ServerMember
from EclipseUser.serializer import EclipseUserSerializer

class ServerMemberSerializer(serializers.ModelSerializer):
    user = EclipseUserSerializer(read_only=True)

    class Meta:
        model = ServerMember
        fields = ['user', 'role']

class ServerMessageSerializer(serializers.ModelSerializer):
    sender = ServerMemberSerializer(read_only=True)

    class Meta:
        model = ServerMessage
        fields = ['server', 'sender', 'content', 'timestamp']
