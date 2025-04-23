import asyncio
import time

# Lock to ensure only one background batch is scheduled at a time
lock = asyncio.Lock()

# Timestamp (monotonic) until which a batch is considered "running"
running_until: float = 0.0 

# Check if a new media batch can be launched
async def can_run_batch(cumulative_delay_sec: int) -> bool:
    global running_until # Make it persistent between requests
    async with lock:
        now = time.monotonic()

        # Deny if still within the time window of a running batch 
        if now < running_until:
            return False

        # Allow and set new "lock window" until this batch completes
        running_until = now + cumulative_delay_sec
        return True

# Return how many seconds are left until the currently running batch is done
def get_remaining_delay() -> int:
    remaining = running_until - time.monotonic()
    return max(int(remaining), 0)
