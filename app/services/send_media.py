import httpx
from app.config.settings import settings
from app.utils.http_client import shared_http_client
from app.utils.time_formatter import format_timestamp
from app.utils.logger import logger

# Send media message {photo + message} to a single group via a HTTP request to EVO API 
def send_media_message(group_id: str, caption: str, media_url: str, evo_delay_ms: int, mediatype: str, mimetype: str):
    url = f"{settings.EVO_C_URL}/message/sendMedia/{settings.INSTANCE_ID}"
    payload = {
        "number": group_id,
        "mediatype": mediatype,
        "mimetype": mimetype,
        "caption": caption,
        "media": media_url,
        "delay": evo_delay_ms,
        "linkPreview": True,
        "mentionsEveryOne": False
    }
    headers = {
        "apikey": settings.API_KEY,
        "Content-Type": "application/json",
        "User-Agent": "WhatsBoost/1.0"
    }

    try:
        response = shared_http_client.post(url, json=payload, headers=headers)
            
        if response.status_code == 201 and "application/json" in response.headers.get("content-type", ""):
            data = response.json()
            key = data.get("key", {})
            msg_id = key.get("id", "N/A")
            timestamp = format_timestamp(data.get("messageTimestamp", "N/A"))
            status = data.get("status", "UNKNOWN")
            logger.info(f"✅ Message sent to group ID: {group_id} | Message ID: {msg_id} at {timestamp} | EVO status: {status}")
            return {"group_id": group_id, "success": True}

        elif response.status_code == 400:
            return {"group_id": group_id, "success": False, "response_status": response.status_code, "response": response.text}
        
        else:
            logger.warning(f"🟡 Unexpected response for group ID: {group_id} | Status code: {response.status_code} | Reason: {response.reason_phrase} \n Headers: {response.headers}")
            return {"group_id": group_id, "success": False, "response_status": response.status_code, "response": response.text}

    except httpx.ReadTimeout:
        logger.warning(f"⏱️ TIMEOUT for {group_id} — EVO API response took too long to respond.")
        return {"group_id": group_id, "success": False, "error": "timeout"}
    
    except Exception as e:
        logger.exception(f"❌ Something went wrong with EVO API response for Group ID: {group_id} | Exception: {str(e)}")
        return {"group_id": group_id, "success": False, "error": str(e)}