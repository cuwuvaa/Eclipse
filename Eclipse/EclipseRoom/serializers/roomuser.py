from rest_framework import serializers
from EclipseRoom.models.roomuser import RoomUser
from EclipseRoom.models.room import Room
from EclipseUser.util.redis import is_user_online
from api.serializers import UserAPISerializer
from django.conf import settings

class RoomUserProfileSerializer(serializers.ModelSerializer):
    displayname = serializers.StringRelatedField(source='user.displayname')
    avatar = serializers.SerializerMethodField()
    is_online = serializers.SerializerMethodField() 
    role = serializers.ChoiceField(choices=RoomUser.ROLE_CHOICES)
    
    class Meta:
        model = RoomUser
        fields = "__all__"

    def get_is_online(self, obj):
        return is_user_online(obj.user.id)
        
    def get_avatar(self, obj):
        if obj.user.avatar and hasattr(obj.user.avatar, 'url'):
            return obj.user.avatar.url
        return None

class RoomSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ('id', 'name', 'description', 'avatar', 'created_at')

    def get_avatar(self, obj):
        if obj.avatar and hasattr(obj.avatar, 'url'):
            return obj.avatar.url
        return None

class RoomUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ('id', 'name', 'description', 'avatar')
        read_only_fields = ('id', 'name')


class RoomUserWithFullUserSerializer(serializers.ModelSerializer):
    user = UserAPISerializer()

    class Meta:
        model = RoomUser
        fields = "__all__"