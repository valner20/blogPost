from rest_framework.viewsets import ModelViewSet
from .models import Post, Comments, Likes 
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

from rest_framework import status
from .permissions import Permissions, IsAuthor
from .serializers import PostSerializer, CommentSerializer, LikeSerializer
from rest_framework.permissions import IsAuthenticated
from .pagination import PostPaginattion, LikesPaginattion, commentsPaginattion
class PostViewSet(ModelViewSet): 
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [Permissions]
    pagination_class = PostPaginattion

    def get_queryset(self):
        user = self.request.user
        permissions = Permissions()
        if user.is_authenticated:
            visible_posts = [post for post in Post.objects.all() if permissions.has_object_permission(self.request, self, post)]
            return Post.objects.filter(id__in=[p.id for p in visible_posts])
        return Post.objects.filter(permissions__gte=8) 
         

    def list(self, request):
        user = self.request.user
        permissions = Permissions()
        
        if user.is_authenticated:
            visible_posts = [post for post in Post.objects.all() if permissions.has_object_permission(request, self, post)]
        else:
            visible_posts = Post.objects.filter(permissions__gte=8)
        
        page = self.paginate_queryset(visible_posts)
        if page is not None:
            serialized = self.get_serializer(page, many=True)
        else:
            serialized = self.get_serializer(visible_posts, many=True)

        data = serialized.data
        if page is not None:
            return self.get_paginated_response(data)
        else:
            return Response({"posts": data})
    

class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsAuthor]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post', 'user']
    pagination_class = commentsPaginattion
    http_method_names = ['get', 'post', 'delete', 'head', 'options']    
    def get_queryset(self):
        user = self.request.user
        permissions = Permissions()
        if user.is_authenticated:
            visiblePosts = [post for post in Post.objects.all().order_by('-created_at') if permissions.has_object_permission(self.request,self, post)]
            visibleComments = Comments.objects.filter(post__in=visiblePosts).order_by('-created_at')
            return visibleComments
        visiblePosts = Post.objects.filter(permissions__gte=8)
        return visibleComments
    

    def retrieve(self, request, pk = None):
        instance = self.get_object()
        if not Permissions().has_object_permission(request, self, instance.post):
            return Response({"detail": "You do not have   to view this comment."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

class LikesViewSet(ModelViewSet):
    queryset = Likes.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated, IsAuthor]
    pagination_class = LikesPaginattion
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post', 'user']
    
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        permissions = Permissions()

        if user.is_authenticated:
            visiblePosts = [
                post for post in Post.objects.all().order_by('id')
                if permissions.has_object_permission(self.request, self, post)
            ]
            return Likes.objects.filter(post__in=visiblePosts).order_by('id')

        visiblePosts = Post.objects.filter(permissions__gte=8)
        return Likes.objects.filter(post__in=visiblePosts).order_by('id')
    

    def retrieve(self, request, pk=None):
        instance = self.get_object()
        if not Permissions().has_object_permission(request, self, instance.post):
            return Response({"detail": "You do not have permission to view this comment."}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    
    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    