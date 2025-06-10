from rest_framework.viewsets import ModelViewSet
from .models import Post, Comments, Likes 
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ParseError
from Users.models import userBlog
from .permissions import Permissions, CanReadOrAuthorDelete, CanRead
from .serializers import PostSerializer, CommentSerializer, LikeSerializer
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
    pagination_class = commentsPaginattion
    http_method_names = ['get', 'post', 'delete', 'head', 'options']    

    def get_queryset(self):
        return AuxQuerySet(self, Comments)

class LikesViewSet(ModelViewSet):
    queryset = Likes.objects.all().order_by('id')
    serializer_class = LikeSerializer
    permission_classes = [CanReadOrAuthorDelete]
    pagination_class = LikesPaginattion
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        return AuxQuerySet(self, Likes)
    




def AuxQuerySet(self,clase):
    post_id = self.request.query_params.get("post")
    user_id = self.request.query_params.get("user")
    permissions = CanRead() 
    request = self.request
    user = request.user

    if user.is_authenticated:
        visible_posts_qs = permissions.get_visible_posts(request, self)
    else:
        visible_posts_qs = Post.objects.filter(permissions__gte=8)

    if post_id:
        try:
            post_id = int(post_id)
        except ValueError:
            raise NotFound("El parámetro 'post' debe ser un número entero.")
        
        if not visible_posts_qs.filter(id=post_id).exists():
            raise NotFound("Not Found")

    if user_id:
        try:
            user_id = int(user_id)
        except ValueError:
            raise ParseError("El parámetro 'user' debe ser un número entero.")

        if not userBlog.objects.filter(id=user_id).exists():
            raise NotFound("Not Found")

    aux = clase.objects.filter(post__in=visible_posts_qs)

    if post_id:
        aux = aux.filter(post_id=post_id)

    if user_id:
        aux = aux.filter(user_id=user_id)

    return aux.order_by('id')