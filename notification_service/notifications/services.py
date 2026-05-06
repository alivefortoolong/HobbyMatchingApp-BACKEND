import requests
from django.conf import settings


def get_user_info(token: str, user_id: int) -> dict:
    url = f"{settings.USER_SERVICE_URL}/api/users/{user_id}/"
    print(f"[DEBUG] Fetching user info from: {url}")  # add this
    try:
        resp = requests.get(
            url,
            headers={'Authorization': f'Bearer {token}'},
            timeout=5,
        )
        print(f"[DEBUG] Status: {resp.status_code}, Body: {resp.text}")  # add this
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException as e:
        print(f"[DEBUG] Request failed: {e}")
    return {}