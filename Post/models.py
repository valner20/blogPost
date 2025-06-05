from django.db import models
from Users.models import userBlog
# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    #usare un entero de permisos para administrar los permisos de los usuarios, este guardara con una base 3 constante para cada permiso
    permissions = models.IntegerField(default=0)  
    author = models.ForeignKey(userBlog, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    excerpt = models.TextField(blank=True)
    def __str__(self):
        return f"{self.title}  by {self.author.username} : {self.content}"
    
    def save(self, *args, **kwargs):
        self.excerpt = self.content[:200]
        super().save(*args, **kwargs)


class Likes(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(userBlog, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('post', 'user') 

    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"
    
class Comments(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(userBlog, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} commented on {self.post.title}: {self.content}"