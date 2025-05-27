from django.db import models
from Users.models import userBlog
# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    permissions = models.IntegerField(default=0)  
    author = models.ForeignKey(userBlog, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return "{title} by {author}" \
        "{content}"


    
#uso una mascara de bits para verificar los permisos, los permisos son ninguno = 0, leer = 1, leer y editar = 2, puedo usar un metodo tipo mascara bits para verificar mis permisos de la request con solo un calculo matematico