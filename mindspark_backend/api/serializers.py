from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
from .models import *


MAX_CONTENT_LENGTH = 65535

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
        fields = ['id', 'source', 'author', 'title', 'description', 'url', 'url_to_image', 
                  'published_at', 'category', 'full_content']

    # Custom validation for full_content length
    def validate_full_content(self, value):
        if len(value) > MAX_CONTENT_LENGTH:
            raise serializers.ValidationError("Content exceeds the maximum allowed length.")
        return value


class BookmarkSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    article = serializers.PrimaryKeyRelatedField(queryset=Article.objects.all())

    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'article']

    



class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True) 
    rating = serializers.ChoiceField(choices=Review.Rating.choices) 
    article = serializers.PrimaryKeyRelatedField(queryset=Article.objects.all())

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'feedback', 'article', 'sentiment']


class UserActivityLogsSerializer(serializers.ModelField):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = UserActivityLogs
        fields = ['id', 'user', 'keyword', 'count']
        extra_kwargs = {
            'count': {'required': False, 'allow_blank': True}, 
            
        }

