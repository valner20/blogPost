from rest_framework import serializers
from .models import userBlog, teams
from django.contrib.auth.hashers import identify_hasher

class Userserializer(serializers.ModelSerializer):
    class Meta:
        model = userBlog
        fields = ['username', 'password','email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = userBlog(**validated_data)
        user.set_password(password)
        user.save()
        return user
        

    
    
class teamSerializer(serializers.ModelSerializer):
    class Meta:
        model = teams
        fields = ['name', 'created_at']
        read_only_fields = ['created_at']
