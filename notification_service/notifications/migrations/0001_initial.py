from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id',           models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('user_id',      models.IntegerField(db_index=True)),
                ('from_user_id', models.IntegerField(null=True, blank=True)),
                ('notif_type',   models.CharField(max_length=20, choices=[('like','Liked your profile'),('match','New match')])),
                ('message',      models.TextField()),
                ('read',         models.BooleanField(default=False)),
                ('created_at',   models.DateTimeField(auto_now_add=True)),
            ],
            options={'db_table': 'notifications', 'ordering': ['-created_at']},
        ),
    ]