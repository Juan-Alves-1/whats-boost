import asyncio
import random
import httpx
import traceback
from datetime import datetime
from app.config.settings import settings
from app.utils.http_client import shared_http_client
import logging


logger = logging.getLogger("media_service")  # Name it per module
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Auxilary function for dynamic EVO API presence (delay)
# characters per second
average_typer = 6 
fast_typer = 9 
super_typer = 12
copy_paste_typer = 16
def get_typing_range_ms(caption) -> tuple:
    length = len(caption)
    try: 
        min_time = (length / copy_paste_typer) * 1000
        max_time = (length / super_typer) * 1000
        return round(min_time), round(max_time)
    except Exception:
        return "Unable to get dynamic WhatsApp presence"

# Format timestamp for logging readability
def format_timestamp(ts: str) -> str:
    try:
        return datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return "Invalid timestamp"

# Send media message {photo + message} to a single group with EVO-API and staggered server delay
async def send_media_message(group_id: str, caption: str, media_url: str, evo_delay_ms: int, server_delay_sec: int, mediatype: str, mimetype: str):
    await asyncio.sleep(server_delay_sec)

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

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = await shared_http_client.post(url, json=payload, headers=headers)
                
            if response.status_code == 201 and "application/json" in response.headers.get("content-type", ""):
                data = response.json()
                key = data.get("key", {})
                msg_id = key.get("id", "N/A")
                timestamp = format_timestamp(data.get("messageTimestamp", "N/A"))
                status = data.get("status", "UNKNOWN")
                logger.info(f"✅ Message sent to group ID: {group_id} | Message ID: {msg_id} at {timestamp} | EVO status: {status}")
                return {"group_id": group_id, "success": True}
            
            elif response.status_code == 400:
                logger.warning(f"🔁 Status: 400 | Group ID: {group_id}, attempt {attempt + 1}/{max_retries}. Retrying... | Response: {response.text}")
                await asyncio.sleep(2 ** attempt + 1)
                continue

            else:
                logger.warning(f"🟡 Unexpected response for group ID: {group_id} | Status code: {response.status_code} | Reason: {response.reason_phrase} \n Headers: {response.headers}")
                return {"group_id": group_id, "success": False, "response": response.text}

        except httpx.ReadTimeout:
            logger.warning(f"⏱️ TIMEOUT for {group_id} — EVO took too long to respond.")
            return {"group_id": group_id, "success": False, "error": "timeout"}
        except Exception as e:
            logger.exception(f"❌ {group_id} | Exception: {str(e)}")
            return {"group_id": group_id, "success": False, "error": str(e)}
        
    logger.exception(f"❌ Group ID: {group_id} | All {max_retries} retries failed with status 400.")
    return {"group_id": group_id, "success": False, "error": "Max retries exceeded"}

# Schedule media tasks with staggered delay
async def send_group_media_messages(group_ids: list[str], caption: str, media_url: str, min_delay_sec: int, max_delay_sec:int, mediatype: str, mimetype: str):
    tasks = []
    total_server_delay = 0
    buffer_between = 1
    min_typing_delay_ms, max_typing_delay_ms = get_typing_range_ms(caption)

    for group_id in group_ids:
        evo_typing_delay_ms = random.randint(min_typing_delay_ms, max_typing_delay_ms)
        evo_typing_delay_sec = evo_typing_delay_ms / 1000
        print(f"📝 Scheduling media to {group_id} in {total_server_delay}s")

        task = asyncio.create_task(send_media_message(
            group_id=group_id,
            caption=caption,
            media_url=media_url,
            evo_delay_ms=evo_typing_delay_ms,
            server_delay_sec=total_server_delay,
            mediatype=mediatype,
            mimetype=mimetype
        ))
        tasks.append(task)
        total_server_delay += evo_typing_delay_sec + buffer_between

    print("🚀 All media tasks scheduled. Awaiting execution...\n")

    try:
        results = await asyncio.gather(*tasks, return_exceptions=True) # Manually handles failed results to avoid crashing the entire endpoint
        print("\n✅ All media tasks completed.\n")
    except Exception as e:
        print(f"❌ BATCH ERROR: {str(e)}")
        traceback.print_exc()
        results = []
    return results
