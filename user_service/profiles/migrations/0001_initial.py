from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Hobby',
            fields=[
                ('id',         models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name',       models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'db_table': 'hobbies', 'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id',           models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('user_id',      models.IntegerField(unique=True, db_index=True)),
                ('nom',          models.CharField(max_length=100, blank=True)),
                ('prenom',       models.CharField(max_length=100, blank=True)),
                ('age',          models.IntegerField(
                    null=True, blank=True,
                    validators=[
                        django.core.validators.MinValueValidator(18),
                        django.core.validators.MaxValueValidator(99),
                    ]
                )),
                ('town',         models.CharField(max_length=100, blank=True)),
                ('gender',       models.CharField(max_length=1, blank=True,
                    choices=[('M','Male'),('F','Female'),('O','Other')])),
                ('bio',          models.TextField(blank=True)),
                ('photo',        models.ImageField(upload_to='photos/', null=True, blank=True)),
                ('social_link', models.URLField(blank=True)),
                ('pref_gender',  models.CharField(max_length=1, default='A',
                    choices=[('M','Male'),('F','Female'),('O','Other'),('A','Any')])),
                ('pref_age_min', models.IntegerField(default=18)),
                ('pref_age_max', models.IntegerField(default=99)),
                ('created_at',   models.DateTimeField(auto_now_add=True)),
                ('updated_at',   models.DateTimeField(auto_now=True)),
                ('hobbies',      models.ManyToManyField(blank=True, related_name='profiles', to='profiles.hobby')),
            ],
            options={'db_table': 'profiles'},
        ),
    ]