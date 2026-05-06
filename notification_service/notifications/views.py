from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Notification
from .services import get_user_info


class NotifView(APIView):
    permission_classes = []

    def post(self, request, user_id):
        try:
            notifications = Notification.objects.filter(
                user_id=user_id
            ).order_by('-created_at')

            auth_header = request.headers.get('Authorization', '')
            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header

            result = []
            for notif in notifications:
                user_info = get_user_info(token, notif.from_user_id)
                if not user_info:
                   continue
                result.append({
                 'id':           notif.id,
                 'from_user_id': notif.from_user_id,
                 'nom':          user_info.get('nom', ''),
                 'prenom':       user_info.get('prenom', ''),
                 'sexe':         user_info.get('sexe', ''),
                 'hobbies':      user_info.get('hobbies', []),
                 'msg':          notif.message,
                 'type':         notif.notif_type,
                 'read':         notif.read,
                 'created_at':   notif.created_at,
})

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )