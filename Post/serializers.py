from rest_framework import serializers
from .models import Post, Comments, Likes
from .permissions import CanRead

class PostSerializer(serializers.ModelSerializer):
    options = [
        #3 niveles de permisos, cada uno con un valor diferente esto me asegura que puedo formar el entero de permisos en base a los niveles de permisos
        (2, "read_and_write"),
        (1, "read_only"),
        (0, "none"),
    ]
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    author = serializers.CharField(source='author.username', read_only=True)

    is_public = serializers.ChoiceField(choices=[(1, "read_only"),(0, "none")], write_only=True)
    authenticated = serializers.ChoiceField(choices=options, write_only=True)
    team = serializers.ChoiceField(choices=options, write_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "author",
            "content",

            "created_at",
            "updated_at",
            "is_public",
            "authenticated",
            "team",
            "permissions",
            "like_count",
            "comment_count"
        ]
        read_only_fields = ["id","author" ,"created_at", "updated_at", "permissions", "like_count", "comment_count"]

    
    def validate(self, attrs):
        def calculate_permissions(is_public, authenticated, team):          
            #los condicionales son para asegurar la jerarquia de permisos, si un permiso superior es menor que otro inferior, se ajusta al valor del otro
            if authenticated < is_public:
                authenticated = is_public
            if team < authenticated:
                team = authenticated
            #se forma el entero de permisos, cada permiso tiene un valor diferente, y se multiplica por su base 3 
            return is_public * 9 + authenticated * 3 + team
        
        request = self.context.get("request")
        permissions = calculate_permissions(
        attrs.get("is_public", 0),
        attrs.get("authenticated", 0),
        attrs.get("team", 0),
            )
        attrs["permissions"] = permissions
        if request.method == "POST":
            attrs["author"] = request.user

        return attrs 
    
    def create(self, validated_data):
        validated_data.pop("is_public", None)
        validated_data.pop("authenticated", None)
        validated_data.pop("team", None)
        request = self.context.get("request")
        if request:
            validated_data["author"] = request.user
        if len(validated_data["content"]) > 200:
                validated_data["content"] = validated_data["content"][:200] + "..."
        return super().create(validated_data)
    
    def get_like_count(self, obj):
        return obj.likes.count()

    def get_comment_count(self, obj):
        return obj.comments.count()

class CommentSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.none())
    postTitle = serializers.CharField(source='post.title', read_only=True)
    user = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Comments
        fields = ['id', 'post','postTitle', 'user', 'content', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            permissions = CanRead()
            self.fields['post'].queryset = permissions.get_visible_posts(request, self)

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class LikeSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.none())
    class Meta:
        model = Likes
        fields = ['id', 'post', 'user']
        read_only_fields = ['id', 'user']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            permissions = CanRead()
            self.fields['post'].queryset = permissions.get_visible_posts(request, self)

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)