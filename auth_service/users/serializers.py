import requests
from rest_framework import serializers
from .models import User
from django.conf import settings


class RegisterSerializer(serializers.ModelSerializer):
    password    = serializers.CharField(write_only=True, min_length=8)
    age         = serializers.IntegerField(required=False)
    town        = serializers.CharField(max_length=100, required=False, allow_blank=True)
    social_link = serializers.URLField(required=False, allow_blank=True)
    pref_age_min = serializers.IntegerField(required=False, default=18)
    pref_age_max = serializers.IntegerField(required=False, default=99)
    pref_gender = serializers.CharField(max_length=1, required=False, allow_blank=True)
    hobbies     = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )

    class Meta:
        model  = User
        fields = [
            'email', 'password',
            'nom', 'prenom', 'gender',
            'age', 'town', 'social_link',
            'pref_age_min', 'pref_age_max', 'pref_gender',
            'hobbies',
        ]

    def create(self, validated_data):
        # Pop profile-only fields before creating the auth user
        age          = validated_data.pop('age', None)
        town         = validated_data.pop('town', '')
        social_link  = validated_data.pop('social_link', '')
        pref_age_min = validated_data.pop('pref_age_min', 18)
        pref_age_max = validated_data.pop('pref_age_max', 99)
        pref_gender  = validated_data.pop('pref_gender', 'A')
        hobbies      = validated_data.pop('hobbies', [])

        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            nom=validated_data.get('nom', ''),
            prenom=validated_data.get('prenom', ''),
            gender=validated_data.get('gender', ''),
        )

        # Forward profile data to user_service
        self._create_profile(user, age, town, social_link,
                             pref_age_min, pref_age_max, pref_gender, hobbies)

        return user

    def _create_profile(self, user, age, town, social_link,
                        pref_age_min, pref_age_max, pref_gender, hobbies):
        """
        Calls user_service to create the profile right after registration.
        Uses a service-to-service token (the user's own fresh token isn't
        available yet, so we use the internal shared secret header).
        """
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        url = f"{settings.USER_SERVICE_URL}/api/users/me/"
        payload = {
            'nom':          user.nom,
            'prenom':       user.prenom,
            'gender':       user.gender,
            'age':          age,
            'town':         town,
            'social_link':  social_link,
            'pref_age_min': pref_age_min,
            'pref_age_max': pref_age_max,
            'pref_gender':  pref_gender or 'A',
            'hobbies':      hobbies,
        }
        headers = {'Authorization': f'Bearer {access_token}'}
        try:
            requests.post(url, json=payload, headers=headers, timeout=5)
        except requests.RequestException as e:
            print(f"[auth_service] Could not create profile in user_service: {e}")