from rest_framework import serializers
from EclipseUser.models.user import EclipseUser

class UserAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = EclipseUser
        fields = ('id', 'username', 'displayname', 'avatar', 'date_joined')