from rest_framework.viewsets import ModelViewSet
from .models import Post, Comments, Likes 
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

from rest_framework import status
from .permissions import Permissions, CanReadOrAuthorDelete, CanRead
from .serializers import PostSerializer, CommentSerializer, LikeSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
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
    queryset = Likes.objects.all().order_by('id')
    serializer_class = CommentSerializer
    permission_classes = [CanReadOrAuthorDelete]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post', 'user']
    pagination_class = commentsPaginattion
    http_method_names = ['get', 'post', 'delete', 'head', 'options']    

    def get_queryset(self):
            user = self.request.user
            permissions = CanRead()
            if user.is_authenticated:
                visible_posts_qs = permissions.get_visible_posts(self.request, self)
                return Comments.objects.filter(post__in=visible_posts_qs).order_by('-created_at')
            
            visible_posts_qs = Post.objects.filter(permissions__gte=8)
            return Comments.objects.filter(post__in=visible_posts_qs).order_by('-created_at')

class LikesViewSet(ModelViewSet):
    queryset = Likes.objects.all().order_by('id')
    serializer_class = LikeSerializer
    permission_classes = [CanReadOrAuthorDelete]
    pagination_class = LikesPaginattion
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post', 'user']
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        permissions = CanRead()
        if user.is_authenticated:
            visible_posts_qs = permissions.get_visible_posts(self.request, self)
            return Likes.objects.filter(post__in=visible_posts_qs).order_by('id')
        visible_posts_qs = Post.objects.filter(permissions__gte=8)
        return Likes.objects.filter(post__in=visible_posts_qs).order_by('id')
