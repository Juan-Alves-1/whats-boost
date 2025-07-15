from app.worker import celery
from celery.exceptions import Retry, MaxRetriesExceededError
from app.utils.redis_client import get_user_lock_status, acquire_user_lock, release_user_lock, redis_client
from app.utils.media_helpers import get_typing_range_ms
from app.utils.logger import logger
from app.services.send_media import send_media_message
import random
import json
import httpx

# Auxiliary function with Lua script for atomic queue check on Redis
def is_queue_under_limit(queue_key: str, max_size: int) -> bool:
    script = """
    local qkey = KEYS[1]
    local max = tonumber(ARGV[1])
    local len = redis.call("LLEN", qkey)
    if len < max then
        return 1
    else
        return 0
    end
    """
    result = redis_client.eval(script, 1, queue_key, max_size)
    return result == 1


'''
    Step 1 - Queue Management: 
        - Ensure a queue on Redis
        - Verify existing lock on Redis
            - Lock exists: enqueue a task by user (queue_key + payload) to Redis for later call
            - No lock: acquire lock for a user and then fire a batch manager task 
'''
@celery.task
def enqueue_user_media_batch(payload: dict):
    payload_json = json.dumps(payload)
    email = payload["user_email"]
    queue_key = f"queue:user:{email}"
    max_queue_per_user = 10 # Note that 1st batch does not count (n + 1)

    try: 
        max_delay_ms = max(get_typing_range_ms(payload["caption"]) or [3000])  # default fallback to 2s  
        max_delay_s = int(max_delay_ms / 1000)
        length_of_groups = len(payload["group_ids"])
        total_buffer = 1 * length_of_groups
        estimated_batch_duration_s = (length_of_groups * max_delay_s) + total_buffer
        lock_ttl = estimated_batch_duration_s + 30

        if get_user_lock_status(email):
            if not is_queue_under_limit(queue_key, max_queue_per_user):
                logger.warning(f"🚫 Queue limit exceeded for {email}. Rejecting new batch.")
                return "Queue limit exceeded"
            
            try: 
                redis_client.rpush(queue_key, payload_json)
                logger.info(f" ⏳ Batch running for user {email}: queuing batch for deferred execution no longer than {lock_ttl} seconds")
                return "Deferred batch"
            except Exception as e:
                logger.exception(f"Failed to push the payload to Redis for the waiting queue: {str(e)}")
                raise

        # No active batch, attempt to acquire lock
        try:
            lock_acquired = acquire_user_lock(email, ttl=lock_ttl)
        except Exception as e:
            logger.exception(f"Failed to acquire a lock for user {email}: {str(e)}")
            raise

        # Lock acquired successfully → go ahead with the batch queue manager
        if lock_acquired:
            logger.info(f"🚀 Lock acquired for user {email} during {lock_ttl} seconds. Dispatching batch immediately")
            send_user_media_batch.delay(payload)
            return "Dispatched"

    except Exception as e: 
        logger.exception(f"🔥 Something unexpected happened: {str(e)}")
        raise
    

'''
    Step 2 - Macro task manager:
        - Populate each task for an EVO API call in a chain 
        - Ensure subtasks are ordered in a human flow (dynamic delays and typing)
        - Release user lock and check the following batch in the queue
'''

@celery.task
def send_user_media_batch(payload: dict): # rename to enqueue 
    caption = payload["caption"]
    group_ids = payload["group_ids"]
    media_url = payload["media_url"]
    mediatype = payload["mediatype"]
    mimetype = payload["mimetype"]
    email = payload["user_email"]

    try:
        total_server_delay = 0
        min_delay_ms, max_delay_ms = get_typing_range_ms(caption)
        extra_buffer = 0.2

        logger.info(f"⛓️ Dispatching {len(group_ids)} subtasks with staggered delays")
        for group_id in group_ids:
            evo_delay = random.randint(min_delay_ms, max_delay_ms)
            delay_sec = total_server_delay
            # Pre-build each "subtask" with immutable signature
            # Kick execution off of each subtask following their respective countdown
            send_media_message_subtask.si(
                group_id, caption, media_url, evo_delay, mediatype, mimetype
            ).apply_async(countdown=delay_sec)  # run task x seconds after queueing

            total_server_delay += (evo_delay // 1000) + extra_buffer # following task receives the previous delay set
        
        logger.info(f"⏱️ Estimated total batch time for {len(group_ids)} groups: {int(total_server_delay)}s")

        estimated_lock_time = total_server_delay + 75
        logger.info(f"🔓 Scheduling lock release in {int(total_server_delay)} seconds for user {email}")

        release_and_check_queue.apply_async(args=[email], countdown=estimated_lock_time) # Lock is expected to be reased when all subtasks finish (so no overlaps)
        return f"Scheduled the total of {len(group_ids)} subtasks for user {email}"
    
    except Exception as e:
        logger.exception(f"❌ Error while processing batch for {email}: {str(e)}")

'''
    Step 3 - Unit tasks:
        - Wrap each EVO API call as a celery task for persistent work
        - Also known as "subtask"
        - 'Bind' ties the instance to the 1st argument 
            - Then get access to self.retry(), self.request, self.name
        - Implement retry attempt here
'''
@celery.task(bind=True, max_retries=1, default_retry_delay=3)
def send_media_message_subtask(self, group_id, caption, media_url, evo_delay_ms, mediatype, mimetype):
    try:
        logger.info(f"🎯 Starting EVO API call to {group_id}")
        result = send_media_message(
            group_id=group_id,
            caption=caption,
            media_url=media_url,
            evo_delay_ms=evo_delay_ms,
            mediatype=mediatype,
            mimetype=mimetype
        )

        if result.get("response_status") == 404:
            logger.warning(f"🔁 Status 400 from EVO API for {group_id}. Retrying via Celery in {self.default_retry_delay} seconds | Retry #{self.request.retries + 1}...")
            raise self.retry(exc=Exception("Received 400 status code response from EVO API"), countdown=self.default_retry_delay)

        return result
    
    except httpx.ReadTimeout as exc:
        logger.warning(f"🔁 ReadTimeout for group ID: {group_id}. Retrying via Celery in {self.default_retry_delay} seconds | Retry #{self.request.retries + 1}...")
        raise self.retry(exc=exc, countdown=self.default_retry_delay)
    
    except MaxRetriesExceededError:
        logger.error(f"🚫 Max retries exceeded for {group_id}")
        raise

    except Retry:
        raise  # CRITICAL — let Celery handle its own Retry

    except Exception as exc:
            logger.exception(f"🔥 Unexpected error for {group_id}: {exc}")
            raise
    
'''
    Step 4 - auxilary task:
        - Release the lock by user
        - Update the queue by removing previous batch
        - Check if there's anything left in the queue 
        - If so, restart the batch cyclewtih the Redis-stored payload
'''
@celery.task
def release_and_check_queue(email: str):
    queue_key = f"queue:user:{email}"
    release_user_lock(email)
    
    if redis_client.llen(queue_key) > 0:
        next_payload = redis_client.lpop(queue_key)
        if next_payload:
            logger.info(f"📨 Found queued payloads for {email}. Dispatching next batch")
            enqueue_user_media_batch.delay(json.loads(next_payload))
