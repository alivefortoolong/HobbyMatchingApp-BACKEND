from django.db import models


class Notification(models.Model):
    TYPE_CHOICES = [
        ('like',  'Liked your profile'),
        ('match', 'New match'),
    ]

    # user who receives this notification
    user_id      = models.IntegerField(db_index=True)
    # user who triggered the action
    from_user_id = models.IntegerField(null=True, blank=True)

    notif_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message    = models.TextField()
    read       = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"Notif({self.notif_type}) → user {self.user_id}"