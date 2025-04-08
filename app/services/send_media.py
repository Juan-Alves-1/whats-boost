import requests
import time
from app.config.settings import settings

def send_media_message(group_id: str, caption: str, media_url: str, file_name: str, delay: int = 10000, mediatype: str = "image", mimetype: str = "image/jpg"):
    url = f"{settings.EVO_C_URL}/message/sendMedia/{settings.INSTANCE_ID}"
    payload = {
        "number": group_id,
        "mediatype": mediatype,
        "mimetype": mimetype,
        "caption": caption,
        "media": media_url,
        "fileName": file_name,
        "delay": delay,
        "linkPreview": True,
        "mentionsEveryOne": False
    }
    headers = {
        "apikey": settings.API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    return f"Response for group {group_id}: {response.text}"

def send_group_media_messages(group_ids: list[str], caption: str, media_url: str, file_name: str, initial_delay: int = 5000, subsequent_delay: int = 20000, mediatype: str = "image", mimetype: str = "image/jpg"):
    results = []
    for i, group_id in enumerate(group_ids):
        current_delay = initial_delay if i == 0 else subsequent_delay
        time.sleep(current_delay / 1000)  # Waits between calls in seconds and sets the pace for external calls
        result = send_media_message(
            group_id=group_id,
            caption=caption,
            media_url=media_url,
            file_name=file_name,
            delay=current_delay,
            mediatype=mediatype,
            mimetype=mimetype
        )
        print(f"Sending media to {group_id} at {time.time()}")
        results.append(result)
    return results
