from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Hobby(models.Model):
    name       = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hobbies'
        ordering = ['name']

    def __str__(self):
        return self.name


class Profile(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    PREF_CHOICES   = [('M', 'Male'), ('F', 'Female'), ('O', 'Other'), ('A', 'Any')]

    # Links to auth_service user — no FK, just the integer ID
    user_id   = models.IntegerField(unique=True, db_index=True)

    # Basic info
    nom       = models.CharField(max_length=100, blank=True)
    prenom    = models.CharField(max_length=100, blank=True)
    age       = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(18), MaxValueValidator(99)]
    )
    town      = models.CharField(max_length=100, blank=True)
    gender    = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    bio       = models.TextField(blank=True)
    photo     = models.ImageField(upload_to='photos/', null=True, blank=True)

    # Social — only revealed after a match (enforced in matching_service)
    social_link = models.URLField(blank=True)

    # Hobbies
    hobbies   = models.ManyToManyField(Hobby, blank=True, related_name='profiles')

    # Matching preferences
    pref_gender  = models.CharField(max_length=1, choices=PREF_CHOICES, default='A')
    pref_age_min = models.IntegerField(default=18)
    pref_age_max = models.IntegerField(default=99)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profiles'

    def __str__(self):
        return f"Profile(user_id={self.user_id}, {self.prenom} {self.nom})"