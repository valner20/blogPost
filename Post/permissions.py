from rest_framework.permissions import BasePermission, SAFE_METHODS

def permissionsAux(permissions):
# fragmento el entero de permisos en sus componentes, luego lo devuelvo como un diccionario, todo me dara un numero de entre 0 y 2
    is_public = permissions // 9
    permissions %= 9
    authenticated = permissions // 3
    team = permissions % 3
    return {
        "is_public": is_public,
        "authenticated": authenticated,
        "team": team,
    }

class Permissions(BasePermission):
    
    def has_object_permission(self, request,view, obj):
        user = request.user
        perms = permissionsAux(obj.permissions)

        if request.method in ["GET"]:
            return self.has_read_permission(request, view, obj)
        else:
            return self.has_write_permission(request, view, obj)
        

    def has_write_permission(self, request,view, obj):
        user = request.user
        if user.is_staff == True:
            return True
        perms = permissionsAux(obj.permissions)
        if not user.is_authenticated:
            return False

        if user == obj.author:
            return True

        if perms["authenticated"] >= 2:
            return True
        if perms["team"] >= 2 and user.team == obj.author.team:
            return True
        return False
    

    def has_read_permission(self, request, view, obj):
        user = request.user
        if user.is_staff == True:
            return True
        perms = permissionsAux(obj.permissions)
        if user == obj.author:
            return True
        if not user.is_authenticated:
            return perms["is_public"] >= 1
        if perms["authenticated"] >= 1:
            return True
        if perms["team"] >= 1 and user.team == obj.author.team:
            return True
        return False
    

class CanRead(BasePermission):

    def get_visible_posts(self, request, view):
        from Post.models import Post  
        permissions = Permissions()
        return Post.objects.filter(
            id__in=[+
                post.id for post in Post.objects.all()
                if permissions.has_read_permission(request, view, post)
                ]
        )
    
class CanReadOrAuthorDelete(BasePermission):

    def has_permission(self, request, view):
        if request.method == 'POST':
            return bool(request.user and request.user.is_authenticated)

        if request.method in SAFE_METHODS:
            return True

     
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            perms = Permissions()
            return perms.has_read_permission(request, view, obj.post)
        return obj.user == request.user