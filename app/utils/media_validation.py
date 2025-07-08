from .http_client import media_validation_client

def is_image_url(url: str) -> bool:
    try:
        response = media_validation_client.head(url, follow_redirects=True)
        content_type = response.headers.get("content-type", "")
        return content_type.startswith("image/")
    except Exception:
        return False