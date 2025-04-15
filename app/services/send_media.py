import asyncio
import random
import httpx
import traceback
from datetime import datetime
from app.config.settings import settings
from app.utils.http_client import shared_http_client


# Format timestamp for logging readability
def format_timestamp(ts: str) -> str:
    try:
        return datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return "Invalid timestamp"

# Send media to a single group with EVO-API and staggered server delay
async def send_media_message(group_id: str, caption: str, media_url: str, file_name: str, evo_delay_ms: int, server_delay_sec: int, mediatype: str, mimetype: str):
    await asyncio.sleep(server_delay_sec)

    url = f"{settings.EVO_C_URL}/message/sendMedia/{settings.INSTANCE_ID}"
    payload = {
        "number": group_id,
        "mediatype": mediatype,
        "mimetype": mimetype,
        "caption": caption,
        "media": media_url,
        "fileName": file_name,
        "delay": evo_delay_ms,
        "linkPreview": True,
        "mentionsEveryOne": False
    }
    headers = {
        "apikey": settings.API_KEY,
        "Content-Type": "application/json",
        # "User-Agent": "WhatsBoost/1.0 (http://......:8000)"
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
                print(f"✅ Message sent to group ID: {group_id} | Message ID: {msg_id} at {timestamp} | EVO status: {status}")
                return {"group_id": group_id, "success": True}
            
            elif response.status_code == 400:
                print(f"🔁 Status: 400 | Group ID: {group_id}, attempt {attempt + 1}/{max_retries}. Retrying...")
                print(f"Response: {response.text}")
                await asyncio.sleep(2 ** attempt + 1)
                continue

            else:
                print(f"🟡 Unexpected response for group ID: {group_id} | Status code: {response.status_code} | Reason: {response.reason_phrase} \n Headers: {response.headers}")
                return {"group_id": group_id, "success": False, "response": response.text}

        except httpx.ReadTimeout:
            print(f"⏱️ TIMEOUT for {group_id} — EVO took too long to respond.")
            return {"group_id": group_id, "success": False, "error": "timeout"}
        except Exception as e:
            print(f"❌ {group_id} | Exception: {str(e)}")
            return {"group_id": group_id, "success": False, "error": str(e)}
        
    print(f"❌ Group ID: {group_id} | All {max_retries} retries failed with status 400.")
    return {"group_id": group_id, "success": False, "error": "Max retries exceeded"}

# Schedule media tasks with staggered delay
async def send_group_media_messages(group_ids: list[str], caption: str, media_url: str, file_name: str, min_delay_sec: int = 25, max_delay_sec: int = 35, mediatype: str = "image", mimetype: str = "image/jpg"):
    total_server_delay = 0
    tasks = []

    for group_id in group_ids:
        evo_typing_delay_ms = random.randint(min_delay_sec * 1000, max_delay_sec * 1000)
        delay_gap = random.randint(min_delay_sec, max_delay_sec)
        total_server_delay += delay_gap
        print(f"📝 Scheduling media to {group_id} in {total_server_delay}s")

        task = asyncio.create_task(send_media_message(
            group_id=group_id,
            caption=caption,
            media_url=media_url,
            file_name=file_name,
            evo_delay_ms=evo_typing_delay_ms,
            server_delay_sec=total_server_delay,
            mediatype=mediatype,
            mimetype=mimetype
        ))
        tasks.append(task)

    print("🚀 All media tasks scheduled. Awaiting execution...\n")

    try:
        results = await asyncio.gather(*tasks, return_exceptions=True) # Manually handles failed results to avoid crashing the entire endpoint
        print("\n✅ All media tasks completed.\n")
    except Exception as e:
        print(f"❌ BATCH ERROR: {str(e)}")
        traceback.print_exc()
        results = []
    return results
