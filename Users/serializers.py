from rest_framework import serializers
from .models import userBlog, teams
from django.contrib.auth.hashers import make_password

class Userserializer(serializers.ModelSerializer):
    class Meta:
        model = userBlog
        fields = ['username', 'password','email']
        write_only_fields = ['password']

    #def create(self, validated_data):
        #validated_data['password'] = make_password(validated_data['password'])
       # return super().create(validated_data)    

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = userBlog
        fields = ['username', 'email', 'team', 'role']
        read_only_fields = ['role'] 
    
class teamSerializer(serializers.ModelSerializer):
    class Meta:
        model = teams
        fields = ['name', 'created_at']
        read_only_fields = ['created_at']
