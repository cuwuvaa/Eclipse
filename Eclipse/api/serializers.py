from rest_framework import serializers
from EclipseUser.models.user import EclipseUser
from EclipseUser.util.redis import is_user_online

class UserAPISerializer(serializers.ModelSerializer):

    is_online = serializers.SerializerMethodField()

    class Meta:
        model = EclipseUser
        fields = ('id', 'username', 'displayname', 'avatar', 'is_online' ,'date_joined')

    def get_is_online(self, obj):
        return is_user_online(obj.id)