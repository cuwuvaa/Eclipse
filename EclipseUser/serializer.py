from rest_framework import serializers
from .models import CustomUser

class EclipseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'avatar']
    
