from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password

# Create your models here.
class teams(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
       return self.name
    
class userBlog(AbstractUser):
        team = models.ForeignKey(teams, on_delete=models.SET(1),default= 1)
        role = models.CharField(default='blogger')        
        def save(self, *args, **kwargs):
            if self.is_staff:
                self.role = 'admin'
            
            if self._state.adding or not self.password.startswith('pbkdf2_'):
                self.password = make_password(self.password)
            return super().save()
          