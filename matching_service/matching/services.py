"""
services.py
-----------
All HTTP calls to user_service live here.
Views stay clean — they never call requests directly.
"""
import requests
from django.conf import settings


def get_auth_header(token):
    return {'Authorization': f'Bearer {token}'}


def get_suggestions_pool(token, exclude_ids: list) -> list:
    """
    Calls user_service internal endpoint to get candidate profiles
    already filtered by the requesting user's preferences.
    """
    exclude_str = ','.join(str(i) for i in exclude_ids)
    url = f"{settings.USER_SERVICE_URL}/api/users/internal/suggestions-pool/"

    try:
        resp = requests.get(
            url,
            params={'exclude_ids': exclude_str},
            headers=get_auth_header(token),
            timeout=5,
        )
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException:
        pass
    return []


def get_profile(token, user_id: int) -> dict:
    """
    Fetches a public profile from user_service.
    Used to enrich match results with profile data.
    """
    url = f"{settings.USER_SERVICE_URL}/api/users/{user_id}/"
    try:
        resp = requests.get(url, headers=get_auth_header(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException:
        pass
    return {}


def get_full_profile(token, user_id: int) -> dict:
    """
    Same as get_profile but we also want social_link.
    user_service public endpoint already includes it — but
    we label this separately for clarity in match reveal logic.
    """
    return get_profile(token, user_id)
def get_matched_profile(token, user_id: int) -> dict:
    """
    Fetches full profile including social_link.
    Only called after a confirmed match.
    """
    url = f"{settings.USER_SERVICE_URL}/api/users/internal/matched/{user_id}/"
    try:
        resp = requests.get(url, headers=get_auth_header(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException:
        pass
    return {}