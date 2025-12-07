from django.contrib.staticfiles.storage import staticfiles_storage
from rest_framework import serializers
from EclipseUser.models.user import EclipseUser
from EclipseUser.util.redis import is_user_online
from django.conf import settings

class UserAPISerializer(serializers.ModelSerializer):

    is_online = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = EclipseUser
        fields = ('id', 'username', 'displayname', 'avatar', 'is_online' ,'date_joined')

    def get_is_online(self, obj):
        return is_user_online(obj.id)

    def get_avatar(self, obj):
        if obj.avatar and hasattr(obj.avatar, 'url'):
            return obj.avatar.url
        return staticfiles_storage.url('EclipseUser/images/defaults/account.png')