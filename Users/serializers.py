from rest_framework import serializers
from .models import userBlog, teams
from django.contrib.auth.hashers import identify_hasher

class Userserializer(serializers.ModelSerializer):
    class Meta:
        model = userBlog
        fields = ['username', 'password','email']
        write_only_fields = ['password']
        
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = userBlog(**validated_data)
        user.set_password(password)
        user.save()
        return user
        
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = userBlog
        fields = ['username', 'email', 'team', 'role']
        read_only_fields = ['role', 'team']
    
    
class teamSerializer(serializers.ModelSerializer):
    class Meta:
        model = teams
        fields = ['name', 'created_at']
        read_only_fields = ['created_at']
