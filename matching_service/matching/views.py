from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny


from .models import Like, Match
from .services import get_profile
from .publisher import publish_like, publish_match


def _get_token(request):
    return request.META.get('HTTP_AUTHORIZATION', '').split(' ', 1)[-1]


# ──────────────────────────────────────────────
# POST /api/matching/like/
# Send: idT (the liker), idR (the liked)
# Creates a match if mutual
# ──────────────────────────────────────────────
class LikeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        from_id = request.data.get('idT') or request.user.id
        to_id   = request.data.get('idR')

        if not to_id:
            return Response({'error': 'idR is required.'}, status=status.HTTP_400_BAD_REQUEST)

        from_id = int(from_id)
        to_id   = int(to_id)

        if from_id == to_id:
            return Response({'error': 'You cannot like yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        Like.objects.get_or_create(from_user_id=from_id, to_user_id=to_id)
        publish_like(from_id, to_id)

        # Check for mutual like → create match
        mutual = Like.objects.filter(from_user_id=to_id, to_user_id=from_id).exists()
        if mutual:
            user1_id, user2_id = sorted([from_id, to_id])
            match, created = Match.objects.get_or_create(user1_id=user1_id, user2_id=user2_id)
            if created:
                publish_match(user1_id, user2_id)
            return Response({'matched': True, 'match_id': match.id}, status=status.HTTP_201_CREATED)

        return Response({'liked': True}, status=status.HTTP_201_CREATED)


# ──────────────────────────────────────────────
# GET /api/matching/matches/
# fetchMatches — send id (from JWT), receive list of matches
# ──────────────────────────────────────────────
class MatchListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        token = _get_token(request)

        matches = Match.objects.filter(user1_id=user_id) | Match.objects.filter(user2_id=user_id)

        result = []
        for match in matches:
            other_id = match.user2_id if match.user1_id == user_id else match.user1_id
            profile  = get_profile(token, other_id)

            result.append({
                'match_id':   match.id,
                'matched_at': match.created_at,
                'user':       profile,
            })

        return Response(result, status=status.HTTP_200_OK)