from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import userBlog, teams
from .serializers import Userserializer, teamSerializer



   
class UserRegisterViewset(ModelViewSet):
    queryset = userBlog.objects.none()
    serializer_class = Userserializer
    permission_classes = [AllowAny] 

    def create(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            return Response({"message": "You are arleady loged."}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class teamsViewset(ModelViewSet):
    queryset = teams
    serializer_class = teamSerializer
    permission_classes = [IsAuthenticated]