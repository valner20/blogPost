from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import userBlog, teams
from .serializers import Userserializer, ProfileSerializer, teamSerializer

class UserViewset(ModelViewSet):
    queryset = userBlog.objects.all()
    serializer_class = ProfileSerializer

   
class UserRegisterViewset(ModelViewSet):
    queryset = userBlog.objects.none()
    serializer_class = Userserializer
    permission_classes = [AllowAny] 

class teamsViewset(ModelViewSet):
    queryset = teams
    serializer_class = teamSerializer
    permission_classes = [IsAuthenticated]