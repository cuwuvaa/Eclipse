from rest_framework import generics, status
from EclipseUser.serializers.user import UserRegistrationSerializer, UserProfileSerializer
from EclipseUser.models.user import EclipseUser
from rest_framework.response import Response


class UserRegisterAPI(generics.CreateAPIView):
    queryset = EclipseUser.objects.all()
    serializer_class = UserRegistrationSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'message': 'Пользователь успешно зарегистрирован'
        }, status=status.HTTP_201_CREATED)
    
class UserListAPI(generics.ListAPIView):
    queryset = EclipseUser.objects.all()
    serializer_class = UserProfileSerializer