from django.db import models


class Like(models.Model):
    from_user_id = models.IntegerField(db_index=True)
    to_user_id   = models.IntegerField(db_index=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table        = 'likes'
        unique_together = ('from_user_id', 'to_user_id')

    def __str__(self):
        return f"Like {self.from_user_id} → {self.to_user_id}"


class Dislike(models.Model):
    from_user_id = models.IntegerField(db_index=True)
    to_user_id   = models.IntegerField(db_index=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table        = 'dislikes'
        unique_together = ('from_user_id', 'to_user_id')

    def __str__(self):
        return f"Dislike {self.from_user_id} → {self.to_user_id}"


class Match(models.Model):
    user1_id   = models.IntegerField(db_index=True)
    user2_id   = models.IntegerField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table        = 'matches'
        unique_together = ('user1_id', 'user2_id')

    def __str__(self):
        return f"Match {self.user1_id} ↔ {self.user2_id}"