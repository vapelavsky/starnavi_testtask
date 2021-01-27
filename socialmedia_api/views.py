import datetime

import requests
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from socialmedia_api.helpers.helpers import get_user_id_from_jwt
from socialmedia_api.serializers import PostSerializer, LikePostSerializer, DislikePostSerializer, \
    UserActivitySerializer
from .models import DislikePost, LikePost, Post, UserActivity


@api_view(['POST'])
def user_signup(request):
    data = request.data
    if 'email' in data:
        email = data['email']
    else:
        content = {'error': 'no email'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if 'username' in data and data['username'] is not None and len(data['username']) > 0:
        username = data['username']
    else:
        content = {'error': "No username"}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if 'password' in data and data['password'] is not None and len(data['password']) > 0:
        password = data['password']
    else:
        content = {'error': "No password"}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    is_username_used = User.objects.filter(username=username)
    if not is_username_used:
        hashed_password = make_password(password)
        new_user = User(email=email, password=hashed_password, username=username)
        new_user.save()
        user = User.objects.get(username=username)
        date = datetime.datetime.now()
        user_activity = UserActivity(user_id=user.id, date=date)
        user_activity.save()

        auth.login(request, user)
        data = {"username": username, "password": password}
        response = requests.post('http://127.0.0.1:8000/api/token/', data=data)
        return Response(response.json(), status=status.HTTP_201_CREATED)
    else:
        content = {'error': 'This username is used'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)


@api_view(["post"])
def login_view(request):
    data = request.data
    if 'username' in data and data['username'] is not None and len(data['username']) > 0:
        username = data['username']
    else:
        content = {'error': "No username"}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if 'password' in data and data['password'] is not None and len(data['password']) > 0:
        password = data['password']
    else:
        content = {'error': "No password"}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    is_user_exist = User.objects.get(username=username)

    auth.login(request, is_user_exist)
    if is_user_exist:
        user_activity = UserActivity.objects.filter(user_id=is_user_exist.id).update(date=datetime.datetime.now())
        data = {"username": username, "password": password}
        response = requests.post('http://127.0.0.1:8000/api/token/', data=data)
        return Response(response.json(), status=status.HTTP_200_OK)
    else:
        content = {'error': "user is not valid"}
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def create_post(request):
    if "Authorization" in request.headers:
        # getting user_id from jwt token
        user_id = get_user_id_from_jwt(request.headers['Authorization'])
        data = request.data
        # checking all data from request
        if 'title' in data and data['title'] is not None and len(data['title']) > 0:
            title = data['title']
        else:
            content = {'error': "No title"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        if 'post' in data and data['post'] is not None and len(data['post']) > 0:
            post = data['post']
        else:
            content = {'error': "No post"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        # add data to db and return details
        new_post = Post(user_id=user_id, title=title, post=post, date_created=datetime.datetime.now())
        new_post.save()
        user_activity = UserActivity.objects.filter(user_id=user_id).update(date=timezone.now())
        post_created = Post.objects.filter(user_id=user_id, title=title, post=post)
        serializer = PostSerializer(post_created, many=True)
        return Response(serializer.data)
    else:
        content = {"error": "No JWT"}
        return Response(content, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def post_like_save(request):
    if "Authorization" in request.headers:
        user_id = get_user_id_from_jwt(request.headers['Authorization'])
        data = request.data
        if 'post_id' in data and data['post_id'] is not None:
            post_id = data['post_id']
        else:
            content = {'error': "No post_id"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        new_like = LikePost(post_id=post_id, user_id=user_id, date=datetime.datetime.now())
        new_like.save()
        user_activity = UserActivity.objects.filter(user_id=user_id).update(date=timezone.now())
        post = Post.objects.get(id=post_id)
        serializer = PostSerializer(post)
        return Response(serializer.data)
    else:
        content = {"error": "No JWT"}
        return Response(content, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def post_dislike_save(request):
    if "Authorization" in request.headers:
        user_id = get_user_id_from_jwt(request.headers['Authorization'])
        data = request.data
        if 'post_id' in data and data['post_id'] is not None:
            post_id = data['post_id']
        else:
            content = {'error': "No post_id"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        new_dislike = DislikePost(post_id=post_id, user_id=user_id, date=datetime.datetime.now())
        new_dislike.save()
        user_activity = UserActivity.objects.filter(user_id=user_id).update(date=timezone.now())
        post = Post.objects.get(id=post_id)
        serializer = PostSerializer(post)
        return Response(serializer.data)
    else:
        content = {"error": "No JWT"}
        return Response(content, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def analytics(request):
    if "Authorization" in request.headers:
        user_id = get_user_id_from_jwt(request.headers['Authorization'])
        user_activity = UserActivity.objects.filter(user_id=user_id).update(date=timezone.now())
        try:
            date_from = request.GET["date_from"]
            date_to = request.GET["date_to"]
        except(TypeError, ValueError, OverflowError):
            content = {'error': 'No date from or date to'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        # getting all satisfied by data likes and dislikes from table
        likes = LikePost.objects.filter(date__range=[date_from, date_to])
        dislikes = DislikePost.objects.filter(date__range=[date_from, date_to])
        return Response({
            'likes': LikePostSerializer(likes, many=True, context={'request': request}).data,
            'dislikes': DislikePostSerializer(dislikes, many=True, context={"request": request}).data,
        })
    else:
        content = {"error": "No JWT"}
        return Response(content, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def get_all_posts(request):
    if "Authorization" in request.headers:
        user_id = get_user_id_from_jwt(request.headers['Authorization'])
        user_activity = UserActivity.objects.filter(user_id=user_id).update(date=timezone.now())
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    else:
        content = {"error": "No JWT"}
        return Response(content, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def user_activity(request):
    if "Authorization" in request.headers:
        user_id = get_user_id_from_jwt(request.headers['Authorization'])
        user_activity = UserActivity.objects.filter(user_id=user_id).update(date=timezone.now())
        if "username" in request.GET:
            user = User.objects.filter(username=request.GET['username'])
            if not user:
                content = {'error': "user is not valid"}
                return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                serializer = UserActivitySerializer(user)
                return Response(serializer.data)
        elif "user_id" in request.GET:
            user = User.objects.get(id=request.GET["user_id"])
            if not user:
                content = {'error': "user is not valid"}
                return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                serializer = UserActivitySerializer(user)
                return Response(serializer.data)
        else:
            users = User.objects.all()
            serializer = UserActivitySerializer(users, many=True)
            return Response(serializer.data)
    else:
        content = {"error": "No JWT"}
        return Response(content, status=status.HTTP_401_UNAUTHORIZED)
