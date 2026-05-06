from django.contrib import admin
from .models import Like, Dislike, Match


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['from_user_id', 'to_user_id', 'created_at']


@admin.register(Dislike)
class DislikeAdmin(admin.ModelAdmin):
    list_display = ['from_user_id', 'to_user_id', 'created_at']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['user1_id', 'user2_id', 'created_at']