from rest_framework.viewsets import ModelViewSet
from .models import Post
from .permissions import Permissions
from .serializers import PostSerializer
class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes= [Permissions]



    