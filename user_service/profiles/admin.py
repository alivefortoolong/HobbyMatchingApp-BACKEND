from django.contrib import admin
from .models import Profile, Hobby


@admin.register(Hobby)
class HobbyAdmin(admin.ModelAdmin):
    list_display  = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display  = ['user_id', 'prenom', 'nom', 'age', 'town', 'gender']
    list_filter   = ['gender', 'pref_gender']
    search_fields = ['nom', 'prenom', 'town']
    filter_horizontal = ['hobbies']