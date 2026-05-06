from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny

from .models import Profile, Hobby
from .serializers import (
    ProfileCreateSerializer,
    PublicProfileSerializer,
    EditPrefSerializer,
    GetPrefSerializer,
)


# ──────────────────────────────────────────────
# POST /api/users/me/
# Called by auth_service right after registration
# Creates the profile with all fields at once
# ──────────────────────────────────────────────
class CreateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.user.id

        # Avoid duplicate profiles (idempotent)
        if Profile.objects.filter(user_id=user_id).exists():
            return Response({'error': 'Profile already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProfileCreateSerializer(data=request.data)
        if serializer.is_valid():
            profile = serializer.save(user_id=user_id)
            return Response(PublicProfileSerializer(profile).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────────
# GET /api/users/<id>/
# fetchUser — returns id, nom, prenom, sexe, age, ville, link, hobbies
# ──────────────────────────────────────────────
class FetchUserView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        try:
            profile = Profile.objects.get(user_id=user_id)
        except Profile.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PublicProfileSerializer(profile)
        return Response(serializer.data)


# ──────────────────────────────────────────────
# GET /api/users/
# fetchUsers — returns all users: id, nom, prenom, age, sexe, ville, hobbies
# ──────────────────────────────────────────────
class FetchUsersView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        profiles   = Profile.objects.exclude(user_id=request.user.id)
        serializer = PublicProfileSerializer(profiles, many=True)
        return Response(serializer.data)


# ──────────────────────────────────────────────
# PATCH /api/users/preferences/
# editPref — send id, prefGender, minAge, maxAge, hobbies
# ──────────────────────────────────────────────
class EditPrefView(APIView):
    permission_classes = []  

    def patch(self, request):

        user_id = request.data.get('user_id')

        if not user_id:
            return Response(
                {'error': 'user_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            profile = Profile.objects.get(user_id=user_id)
        except Profile.DoesNotExist:
            return Response(
                {'error': 'Profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = EditPrefSerializer(
            profile,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                GetPrefSerializer(profile).data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# ──────────────────────────────────────────────
# GET /api/users/preferences/
# getPref — send id (from JWT), receive prefGender, minAge, maxAge, ville, hobbies
# ──────────────────────────────────────────────
class GetPrefView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        try:
            profile = Profile.objects.get(user_id=user_id)
        except Profile.DoesNotExist:
            return Response(
                {'error': 'Profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = GetPrefSerializer(profile)
        return Response(serializer.data)