from rest_framework import generics, status
from django.http import Http404
from rest_framework.response import Response

from api.serializers import UserAPISerializer
from EclipseUser.models.user import EclipseUser

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

class UserListAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = EclipseUser.objects.all()
    serializer_class = UserAPISerializer

class UserDataAPI(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return EclipseUser.objects.get(pk=pk)
        except EclipseUser.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = UserAPISerializer(snippet)
        return Response(serializer.data, status=status.HTTP_200_OK)


