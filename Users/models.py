from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import identify_hasher
# Create your models here.
class teams(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
       return self.name
    
class userBlog(AbstractUser):
        team = models.ForeignKey(teams, on_delete=models.SET(1), null = True)
        role = models.CharField(default='blogger')   
        email = models.EmailField(unique=True)     

        USERNAME_FIELD = 'email'
        REQUIRED_FIELDS = ['username']


        def save(self, *args, **kwargs):
            if not self.team:
                self.team,_ = teams.objects.get_or_create(id = 1, defaults={'name': 'default'})

            if self.is_staff:
                self.role = 'admin'          
            if self._state.adding:
                try:
                    identify_hasher(self.password)
                except Exception:
                    self.set_password(self.password)
            return super().save(*args, **kwargs)
          