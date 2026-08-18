import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import msal
import requests

GRAPH_URL = "https://graph.microsoft.com/v1.0"
PHOTO_DIR = Path("photos")
TIMEZONE = os.getenv("TIMEZONE", "America/Sao_Paulo")

CLIENT_ID = os.environ["MS_CLIENT_ID"]
TENANT_ID = os.getenv("MS_TENANT_ID", "organizations")

def choose_photo():
    photos = sorted(
        p for p in PHOTO_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg"}
    )
    if not photos:
        raise RuntimeError("Coloque pelo menos uma foto JPG/JPEG em ./photos")

    today = datetime.now(ZoneInfo(TIMEZONE)).date()
    return photos[today.toordinal() % len(photos)]

def acquire_token():
    cache = msal.SerializableTokenCache()

    # The cache is restored by the workflow from the TOKEN_CACHE secret.
    encoded_cache = os.getenv("MS_TOKEN_CACHE", "")
    if encoded_cache:
        cache.deserialize(encoded_cache)

    app = msal.PublicClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        token_cache=cache,
    )

    scopes = ["User.ReadWrite", "offline_access", "openid", "profile"]

    accounts = app.get_accounts()
    result = None

    if accounts:
        result = app.acquire_token_silent(scopes, account=accounts[0])

    if not result:
        # First run: authenticate interactively with device code.
        flow = app.initiate_device_flow(scopes=scopes)
        if "user_code" not in flow:
            raise RuntimeError(f"Falha ao iniciar login: {flow}")

        print(flow["message"])
        result = app.acquire_token_by_device_flow(flow)

    if "access_token" not in result:
        raise RuntimeError(
            "Falha no login: " +
            str(result.get("error_description", result))
        )

    # Persist cache outside the repo so the next run can refresh the token.
    if cache.has_state_changed:
        print("TOKEN_CACHE=" + cache.serialize())

    return result["access_token"]

def update_photo(photo, token):
    url = f"{GRAPH_URL}/me/photo/$value"

    with photo.open("rb") as f:
        response = requests.put(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "image/jpeg",
            },
            data=f,
            timeout=60,
        )

    if response.status_code not in (200, 204):
        raise RuntimeError(
            f"Graph HTTP {response.status_code}: {response.text}"
        )

def main():
    photo = choose_photo()
    print(f"Foto escolhida: {photo.name}")
    token = acquire_token()
    update_photo(photo, token)
    print("Foto atualizada com sucesso.")

if __name__ == "__main__":
    main()
