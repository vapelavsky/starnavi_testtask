
from django.urls import path
from . import views

urlpatterns = [
    path('api/signup/', views.user_signup, name='register_user'),
    path('api/login/', views.login_view, name='login'),
    path('api/create-post/', views.create_post, name='create_post'),
    path('api/post-like/', views.post_like_save, name='post_like_save'),
    path('api/post-dislike/', views.post_dislike_save, name='post_dislike_save'),
    path('api/analytics/', views.analytics, name='analytics'),
    path('api/get-all-posts/', views.get_all_posts, name='get_all_posts'),
    path('api/user-activity/', views.user_activity, name='user_activity')
]