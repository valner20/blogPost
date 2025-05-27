from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    options = [
        (2, "read_and_write"),
        (1, "read_only"),
        (0, "none"),
    ]
    is_public = serializers.ChoiceField(choices=[(1, "read_only"),(0, "none")], write_only=True)
    authenticated = serializers.ChoiceField(choices=options, write_only=True)
    team = serializers.ChoiceField(choices=options, write_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "created_at",
            "updated_at",
            "is_public",
            "authenticated",
            "team",
            "permissions"
        ]
        read_only_fields = ["id", "created_at", "updated_at", "permissions"]

    def validate(self, attrs):
        def calculate_permissions(is_public, authenticated, team):            
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
        return super().create(validated_data)
