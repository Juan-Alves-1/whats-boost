import requests
from app.config.settings import settings

# Sends a text message to a single group
def send_text_message(group_id: str, message_text: str, delay: int): 
    url = f"{settings.EVO_C_URL}/message/sendText/{settings.INSTANCE_ID}"
    payload = {
        "number": group_id,
        "text": message_text,
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

# Sends text messages to a list of groups
def send_group_text_messages(group_ids: list[str], message_text: str, initial_delay: int = 5000, subsequent_delay: int = 20000):
    results = []
    for i, group_id in enumerate(group_ids):
        current_delay = initial_delay if i == 0 else subsequent_delay
        result = send_text_message(group_id, message_text, current_delay)
        results.append(result)
    return results


