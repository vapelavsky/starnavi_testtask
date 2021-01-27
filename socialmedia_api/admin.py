from django.contrib import admin
from .models import Post, DislikePost, LikePost, UserActivity

# Register your models here.
admin.site.register(Post)
admin.site.register(LikePost)
admin.site.register(DislikePost)
admin.site.register(UserActivity)