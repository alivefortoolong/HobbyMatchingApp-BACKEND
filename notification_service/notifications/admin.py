from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ['user_id', 'from_user_id', 'notif_type', 'read', 'created_at']
    list_filter   = ['notif_type', 'read']
    search_fields = ['user_id', 'from_user_id']