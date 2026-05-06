from django.urls import path
from .views import (
    CreateProfileView,
    FetchUserView,
    FetchUsersView,
    EditPrefView,
    GetPrefView,
)

urlpatterns = [
    # Called by auth_service right after registration
    path('me/',                CreateProfileView.as_view(), name='create-profile'),

    # fetchUsers — all users (for suggestions/browse)
    path('',                   FetchUsersView.as_view(),    name='fetch-users'),

    # fetchUser — single user by id
    path('<int:user_id>/',     FetchUserView.as_view(),     name='fetch-user'),

    # getPref — get current user's preferences
    path('preferences/<int:user_id>/',       GetPrefView.as_view(),       name='get-pref'),

    # editPref — update preferences
    path('preferences/edit/',  EditPrefView.as_view(),      name='edit-pref'),
]