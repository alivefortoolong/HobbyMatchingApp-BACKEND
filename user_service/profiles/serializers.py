from rest_framework import serializers
from .models import Profile, Hobby


# ──────────────────────────────────────────────
# Used by POST /me/ (called from auth_service on register)
# ──────────────────────────────────────────────
class ProfileCreateSerializer(serializers.ModelSerializer):
    hobbies = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False, default=list
    )

    class Meta:
        model  = Profile
        fields = [
            'nom', 'prenom', 'gender', 'age', 'town',
            'social_link', 'pref_gender', 'pref_age_min', 'pref_age_max',
            'hobbies',
        ]

    def create(self, validated_data):
        hobby_names = validated_data.pop('hobbies', [])
        profile     = Profile.objects.create(**validated_data)

        for name in hobby_names:
            hobby, _ = Hobby.objects.get_or_create(name=name.strip())
            profile.hobbies.add(hobby)

        return profile


# ──────────────────────────────────────────────
# fetchUser / fetchUsers — public profile with social link
# ──────────────────────────────────────────────
class PublicProfileSerializer(serializers.ModelSerializer):
    hobbies = serializers.SerializerMethodField()
    sexe    = serializers.CharField(source='gender')   # frontend uses "sexe"
    ville   = serializers.CharField(source='town')     # frontend uses "ville"
    link    = serializers.URLField(source='social_link', allow_blank=True)

    class Meta:
        model  = Profile
        fields = ['id', 'user_id', 'nom', 'prenom', 'sexe', 'age', 'ville', 'link', 'hobbies']

    def get_hobbies(self, obj):
        return list(obj.hobbies.values_list('name', flat=True))


# ──────────────────────────────────────────────
# editPref — accepts prefGender, minAge, maxAge, hobbies
# ──────────────────────────────────────────────
class EditPrefSerializer(serializers.ModelSerializer):
    hobbies  = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    minAge   = serializers.IntegerField(source='pref_age_min', required=False)
    maxAge   = serializers.IntegerField(source='pref_age_max', required=False)
    prefGender = serializers.CharField(source='pref_gender', required=False)

    class Meta:
        model  = Profile
        fields = ['prefGender', 'minAge', 'maxAge', 'hobbies']

    def validate(self, data):
        min_age = data.get('pref_age_min', self.instance.pref_age_min if self.instance else 18)
        max_age = data.get('pref_age_max', self.instance.pref_age_max if self.instance else 99)
        if min_age > max_age:
            raise serializers.ValidationError("minAge cannot be greater than maxAge.")
        return data

    def update(self, instance, validated_data):
        hobby_names = validated_data.pop('hobbies', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if hobby_names is not None:
            instance.hobbies.clear()
            for name in hobby_names:
                hobby, _ = Hobby.objects.get_or_create(name=name.strip())
                instance.hobbies.add(hobby)

        return instance


# ──────────────────────────────────────────────
# getPref — returns prefGender, minAge, maxAge, ville, hobbies
# ──────────────────────────────────────────────
class GetPrefSerializer(serializers.ModelSerializer):
    hobbies    = serializers.SerializerMethodField()
    minAge     = serializers.IntegerField(source='pref_age_min')
    maxAge     = serializers.IntegerField(source='pref_age_max')
    prefGender = serializers.CharField(source='pref_gender')
    ville      = serializers.CharField(source='town')

    class Meta:
        model  = Profile
        fields = ['prefGender', 'minAge', 'maxAge', 'ville', 'hobbies']

    def get_hobbies(self, obj):
        return list(obj.hobbies.values_list('name', flat=True))