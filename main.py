import os
import requests

def send_group_messages(group_ids, message_text):
    # Retrieve environment variables
    api_key = os.getenv("API_KEY")
    instance_id = os.getenv("INSTANCE_ID")
    base_url = os.getenv("EVO_C_URL") 

    # Validate that necessary env variables are available
    if not api_key or not instance_id:
        raise ValueError("Missing required environment variables: API_KEY and INSTANCE_ID must be set.")

    # Build the URL using the instance ID
    url = f"{base_url}/message/sendText/{instance_id}"
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }

    # Iterate through the group IDs and send a message for each one
    for group_id in group_ids:
        payload = {
            "number": group_id,
            "text": message_text,
            "delay": 10000,
            "linkPreview": True,
            "mentionsEveryOne": False
        }

        response = requests.post(url, json=payload, headers=headers)
        print(f"Response for group {group_id}: {response.text}")

# Example usage:
if __name__ == "__main__":
    groups = [
        "120363401455758330@g.us",  # Group1
        "120363418573072300@g.us",  # Group2
        "120363399859395527@g.us"   # Group3
    ]
    # send_group_messages(groups, "function test with base_url as env variable")
