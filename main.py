import os
import requests

def get_env_config():
    api_key = os.getenv("API_KEY")
    instance_id = os.getenv("INSTANCE_ID")
    base_url = os.getenv("EVO_C_URL")
    
    if not api_key or not instance_id or not base_url:
        raise ValueError("Missing one or more required environment variables: API_KEY, INSTANCE_ID, EVO_C_URL must be set.")
    
    return {
        "api_key": api_key,
        "instance_id": instance_id,
        "base_url": base_url,
        "headers": {
            "apikey": api_key,
            "Content-Type": "application/json"
        }
    }

# Sends a text message to a single group
def send_text_message(config, group_id, message_text, delay): 
    url = f"{config['base_url']}/message/sendText/{config['instance_id']}"
    payload = {
        "number": group_id,
        "text": message_text,
        "delay": delay,
        "linkPreview": True,
        "mentionsEveryOne": False
    }
    response = requests.post(url, json=payload, headers=config["headers"])
    return f"Response for group {group_id}: {response.text}"

# Sends a media message (image + text) to a single group
def send_media_message(config, group_id, caption, media_url, file_name, delay, mediatype="image", mimetype="image/jpg"):
    url = f"{config['base_url']}/message/sendMedia/{config['instance_id']}"
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
    response = requests.post(url, json=payload, headers=config["headers"])
    return f"Response for group {group_id}: {response.text}"

# Sends text messages to a list of groups
def send_group_text_messages(group_ids, message_text, initial_delay=10000, subsequent_delay=70000):
    config = get_env_config()
    for i, group_id in enumerate(group_ids):
        current_delay = initial_delay if i == 0 else subsequent_delay
        result = send_text_message(config, group_id, message_text, current_delay)
        print(result)

#  Sends media messages to a list of groups.
def send_group_media_messages(group_ids, caption, media_url, file_name, initial_delay=10000, subsequent_delay=70000):
    config = get_env_config()
    for i, group_id in enumerate(group_ids):
        current_delay = initial_delay if i == 0 else subsequent_delay
        result = send_media_message(config, group_id, caption, media_url, file_name, current_delay)
        print(result)

# Example usage:
if __name__ == "__main__":
    groups = [
        "120363401455758330@g.us",  # Group1
        "120363418573072300@g.us",  # Group2
        "120363399859395527@g.us"   # Group3
    ]
    
    # Send text messages to groups
    # send_group_text_messages(groups, "This is a text message test.")
    
    # Send media messages to groups
    send_group_media_messages(
        groups,
        caption="You saw here first! Gradual delay between messages",
        media_url="https://m.media-amazon.com/images/I/71sCg43+nPL._AC_SL1500_.jpg",
        file_name="example.jpg"
    )
