from rest_framework.viewsets import ModelViewSet
from .models import Post
from rest_framework.response import Response
from .permissions import Permissions
from .serializers import PostSerializer
class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [Permissions]
    def list(self, request):
        user = self.request.user
        permissions = Permissions()
        if user.is_authenticated:
            visiblePosts = [post for post in Post.objects.all() if permissions.has_object_permission(request,self, post)]
            return Response({"posts": self.get_serializer(visiblePosts, many=True).data}) 
        visiblePosts = Post.objects.filter(permissions__gte=8)
        return Response({"posts": self.get_serializer(visiblePosts, many=True).data})   

    