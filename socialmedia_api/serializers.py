from django.contrib.auth.models import User
from rest_framework import serializers

from socialmedia_api.models import Post, LikePost, DislikePost, UserActivity


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'last_login', 'date_joined']


class DislikePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = DislikePost
        fields = ['post', 'date']


class LikePostSerializer(serializers.ModelSerializer):

    class Meta:
        model = LikePost
        fields = ['post', 'date']


class PostSerializer(serializers.ModelSerializer):
    post_like = LikePostSerializer(many=True)
    post_dislike = DislikePostSerializer(many=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'title', 'post', 'date_created', 'post_like', 'post_dislike']


class ActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = UserActivity
        fields = ['date']


class UserActivitySerializer(serializers.HyperlinkedModelSerializer):
    last_activity = ActivitySerializer(many=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'last_login', 'last_activity']
