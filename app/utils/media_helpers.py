from app.utils.logger import logger
from app.config.settings import settings

"""
    Estimates a realistic typing delay range for the EVO API 
    based on caption length and human typing speed (cps).
    Returns (min_delay_ms, max_delay_ms).
"""

def get_typing_range_ms(caption: str) -> tuple[int, int]:
    min_speed = int(settings.MIN_TYPING_SPEED)
    max_speed = int(settings.MAX_TYPING_SPEED)
    length = len(caption) 

    if min_speed <= 0 or max_speed <= 0:
        raise ValueError("Typing speeds must be positive integers")

    try: 
        min_time = (length // max_speed) * 1000
        max_time = (length // min_speed) * 1000
        return round(min_time), round(max_time)
    
    except ValueError as e:
        logger.error("Invalid typing speed configuration: %s", e)
    except Exception:
        logger.error("Unable to get dynamic typing for delays (between subtasks) and WhatsApp presence (EVO delay)")
