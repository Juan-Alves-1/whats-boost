from .http_client import shared_http_client

async def is_image_url(url: str) -> bool:
    try:
        response = await shared_http_client.head(url, follow_redirects=True)
        content_type = response.headers.get("content-type", "")
        return content_type.startswith("image/")
    except Exception:
        return False