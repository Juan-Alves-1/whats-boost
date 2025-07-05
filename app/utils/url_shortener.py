from httpx import HTTPStatusError
from app.config.settings import settings
from .http_client import shared_http_client
from app.utils.logger import logger

def create_amazon_shortlink(name: str, long_url: str) -> str:
    endpoint = "https://creators.posttap.com/api/create-shortlink"
    headers = {
        "Accept":       "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin":       "https://creators.posttap.com",
        "Referer":      "https://creators.posttap.com/",
        "Cookie":( 
            f"btn_session={settings.BTN_SESSION};"
            f"btn_session.sig={settings.BTN_SESSION_SIG};"
            f"btn_logged_in={settings.BTN_LOGGED_IN};"
            f"btn_logged_in.sig={settings.BTN_LOGGED_IN_SIG};"
            f"btn_profile_reminder={settings.BTN_PROFILE_REMINDER}"
        ),
    }
    payload = {"name": name, "url": long_url}

    try:
        response = shared_http_client.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
    except HTTPStatusError as exc:
        logger.error(
            "PostTap API returned HTTP %s: %s — falling back to long_url",
            exc.response.status_code,
            exc.response.text,
        )
        return long_url

    shortlink = data.get("object", {}).get("shortlink")
    if not shortlink:
        logger.debug("PostTap payload keys: %s", list(data.keys()))
        logger.error("PostTap API returned unexpected response: %r", data)
        return long_url

    return shortlink

