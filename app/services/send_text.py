import asyncio
import random
import httpx
from datetime import datetime
from app.config.settings import settings


# Formats timestamp for logging readability
def format_timestamp(ts: str) -> str:
    try:
        return datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return "Invalid timestamp"

# Sends a text message to a single group. Planned as a lightweight scheduling queue thanks to accumulated delay (server_delay_sec)
async def send_text_message(group_id: str, message_text: str, evo_delay_ms: int, server_delay_sec: int):
    await asyncio.sleep(server_delay_sec)  # This delay is what staggered the execution
    
    url = f"{settings.EVO_C_URL}/message/sendText/{settings.INSTANCE_ID}"
    payload = {
        "number": group_id,
        "text": message_text,
        "delay": evo_delay_ms,  # EVO simulates the typing with this value
        "linkPreview": True,
        "mentionsEveryOne": False
    }
    headers = {
        "apikey": settings.API_KEY,
        "Content-Type": "application/json"
    }

    timeout = httpx.Timeout(connect=10.0, read=45.0, write=10.0, pool=60.0) # Sets parameters since httpx requests will wait for EVO API response

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload, headers=headers)

        if response.status_code == 201 and "application/json" in response.headers.get("content-type", ""):
            data = response.json()
            key = data.get("key", {})
            msg_id = key.get("id", "N/A")
            timestamp = format_timestamp(data.get("messageTimestamp", ""))
            status = data.get("status", "UNKNOWN")

            print(f"✅ Message sent to group ID: {group_id} | Message ID: {msg_id} at {timestamp} | EVO status: {status}")
            return {"group_id": group_id, "success": True}

        else:
            print(f"⚠️ Unexpected response from EVO API for group ID: {group_id} | Status code: {response.status_code}")
            return {"group_id": group_id, "success": False, "response": response.text}

    except httpx.ReadTimeout:
        print(f"⏱️ TIMEOUT: {group_id} | EVO took too long to respond.")
        return {"group_id": group_id, "success": False, "error": "timeout"}

    except Exception as e:
        print(f"❌ {group_id} | Exception: {str(e)}")
        return {"group_id": group_id, "success": False, "error": str(e)}


# Schedules all tasks 
async def send_group_text_messages(group_ids: list[str], message_text: str, min_delay_sec: int = 12, max_delay_sec: int = 18):
    total_server_delay = 0  
    tasks = []

    for group_id in group_ids:
        evo_typing_delay_ms = random.randint(min_delay_sec * 1000, max_delay_sec * 1000)   # EVO typing simulation in milliseconds
        delay_gap = random.randint(min_delay_sec, max_delay_sec)  # Server staggering: accumulate gap 
        total_server_delay += delay_gap
        print(f"📝 Scheduling message to {group_id} in {total_server_delay}s") 

        # Schedule each coroutine concurrently
        task = asyncio.create_task( 
            send_text_message(
                group_id=group_id,
                message_text=message_text,
                evo_delay_ms=evo_typing_delay_ms,
                server_delay_sec=total_server_delay
            )
        )
        tasks.append(task)

    print("🚀 All message tasks scheduled. Awaiting execution...\n")
    #Investiage: did not return status when the browser was closed, whereas without it it returns the status code on the console immediately
    results = await asyncio.gather(*tasks, return_exceptions=True) # manually handles failed results to avoid crashing the entire endpoint
    print("\n✅ All message tasks completed.\n")
    return results
