from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id',           models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('from_user_id', models.IntegerField(db_index=True)),
                ('to_user_id',   models.IntegerField(db_index=True)),
                ('created_at',   models.DateTimeField(auto_now_add=True)),
            ],
            options={'db_table': 'likes', 'unique_together': {('from_user_id', 'to_user_id')}},
        ),
        migrations.CreateModel(
            name='Dislike',
            fields=[
                ('id',           models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('from_user_id', models.IntegerField(db_index=True)),
                ('to_user_id',   models.IntegerField(db_index=True)),
                ('created_at',   models.DateTimeField(auto_now_add=True)),
            ],
            options={'db_table': 'dislikes', 'unique_together': {('from_user_id', 'to_user_id')}},
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id',         models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('user1_id',   models.IntegerField(db_index=True)),
                ('user2_id',   models.IntegerField(db_index=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'db_table': 'matches', 'unique_together': {('user1_id', 'user2_id')}},
        ),
    ]