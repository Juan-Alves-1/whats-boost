from httpx import ReadTimeout, ConnectTimeout, PoolTimeout, RequestError
from app.config.settings import settings
from app.utils.http_client import evo_client
from app.utils.time_formatter import format_timestamp
from app.utils.logger import logger

# Send media message {photo + message} to a single group via a HTTP request to EVO API 
def send_media_message(group_id: str, caption: str, media_url: str, evo_delay_ms: int, mediatype: str, mimetype: str):
    url = f"{settings.EVO_SERVER_URL}/message/sendMedia/{settings.EVO_INSTANCE_ID}"
    payload = {
        "number": group_id,
        "mediatype": mediatype,
        "mimetype": mimetype,
        "caption": caption,
        "media": media_url,
        "delay": evo_delay_ms,
        "filename": "image.png",
    }
    headers = {
        "apikey": settings.EVO_API_KEY,
        "Content-Type": "application/json",
        "User-Agent": "WhatsBoost/1.0"
    }

    try:
        response = evo_client.post(url, json=payload, headers=headers)
            
        if response.status_code == 201 and "application/json" in response.headers.get("content-type", ""):
            data = response.json()
            key = data.get("key", {})
            msg_id = key.get("id", "N/A")
            timestamp = format_timestamp(data.get("messageTimestamp", "N/A"))
            status = data.get("status", "UNKNOWN")
            logger.info(f"✅ Message sent to group ID: {group_id} | Message ID: {msg_id} at {timestamp} | EVO status: {status}")
            return {"group_id": group_id, "success": True}

        elif response.status_code == 400:
            data = response.json()
            key = data.get("key", {})
            msg_id = key.get("id", "N/A")
            timestamp = format_timestamp(data.get("messageTimestamp", "N/A"))
            status = data.get("status", "UNKNOWN")
            correlation_id = response.headers.get("X-Correlation-Id", "none")

            logger.error(
                "🛑 EVO 400 for %(group_id)s: url=%(url)s, payload=%(payload)s, "
                "key.id=%(msg_id)s, timestamp=%(timestamp)s, status=%(status)s, "
                "correlation_id=%(correlation_id)s, response_body=%(body)s",
                {
                    "group_id":    group_id,
                    "url":         response.url,
                    "payload":     payload,              # whatever dict/json you sent
                    "msg_id":      msg_id,
                    "timestamp":   timestamp,
                    "status":      status,
                    "correlation_id": correlation_id,
                    "body":        data,                 # full parsed JSON
                }
            )
            return {"group_id": group_id, "success": False, "response_status": 400, "response": data, "correlation_id": correlation_id}
        
        else:
            logger.warning(f"🟡 Unexpected response for group ID: {group_id} | Status code: {response.status_code} | Reason: {response.reason_phrase} \n Headers: {response.headers}")
            return {"group_id": group_id, "success": False, "response_status": response.status_code, "response": response.text}

    except ConnectTimeout:
        logger.warning(f"🔌 CONNECT TIMEOUT for group ID: {group_id}")
        return {"group_id": group_id, "success": False, "error": "connect timeout"}
    
    except ReadTimeout:
        logger.warning(f"⏱️  READ TIMEOUT for group ID: {group_id}")
        raise
    
    except PoolTimeout:
        logger.warning(f"🚧  POOL TIMEOUT for group ID: {group_id}")
        return {"group_id": group_id, "success": False, "error": "pool timeout"}
    
    except RequestError as e:
        logger.exception(f"❌  HTTPX REQUEST ERROR to EVO API for Group ID: {group_id} | DETAILS - type: {type(e).__name__} message: {e}")
        return {"group_id": group_id, "success": False, "error": {type(e).__name__}}
    
    except Exception as e:
        logger.exception(f"❌ Something went wrong with EVO API response for Group ID: {group_id} | Exception: {str(e)}")
        return {"group_id": group_id, "success": False, "error": str(e)}