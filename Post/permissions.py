from rest_framework.permissions import BasePermission

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
    

class IsAuthor(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            permissions = Permissions()
            return permissions.has_read_permission(self,request,view, obj)  
        return obj.user == request.user
    
