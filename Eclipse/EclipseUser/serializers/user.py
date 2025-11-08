from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from EclipseUser.models.user import EclipseUser

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EclipseUser
        fields = ('id', 'username', 'email', 'displayname', 'date_joined')

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = EclipseUser
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = EclipseUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user