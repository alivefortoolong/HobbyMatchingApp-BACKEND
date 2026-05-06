from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Notification
        fields = [
            'id',
            'user_id',
            'from_user_id',
            'notif_type',
            'message',
            'read',
            'created_at',
        ]
        read_only_fields = ['id', 'user_id', 'from_user_id', 'notif_type', 'message', 'created_at']