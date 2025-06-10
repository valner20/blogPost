"""
URL configuration for blogPost project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from Users.viewSets import UserRegisterViewset,teamsViewset
from Post.viewSet import PostViewSet, CommentViewSet, LikesViewSet
router = DefaultRouter()
router.register('register',UserRegisterViewset, basename='register') 
router.register('registerTeams',teamsViewset, basename='teams') 
router.register('Post',PostViewSet, basename='Post') 
router.register('comment',CommentViewSet, basename='comment') 
router.register('likes',LikesViewSet, basename='likes') 



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]
