from django.urls import path
from .views import NotifView
 
urlpatterns = [
    path('', NotifView.as_view(), name='notif'),
]