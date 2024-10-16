from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
from .models import *

User = get_user_model()

class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name', 'profile_picture')  
        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False, 'validators': []}, 
            'first_name':  {'required': True, 'allow_blank': False},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    

# Custom serializer for retrieving/updating user details
class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'profile_picture')






class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'source', 'author', 'title', 'description', 'url', 'url_to_image', 'published_at', 'content', 'category', 'full_content']


class BookmarkSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  
    article = ArticleSerializer(read_only=True)  

    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'article']


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True) 
    rating = serializers.ChoiceField(choices=Review.Rating.choices)  

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'feedback']

