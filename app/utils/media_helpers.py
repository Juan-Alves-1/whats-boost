from app.utils.logger import logger

"""
    Estimates a realistic typing delay range for the EVO API 
    based on caption length and human typing speed (cps).
    Returns (min_delay_ms, max_delay_ms).
"""


def get_typing_range_ms(caption: str) -> tuple[int, int]:
    average_typer = 6 
    fast_typer = 8 
    super_typer = 12
    copy_paste_typer = 16
    length = len(caption)

    try: 
        min_time = (length / copy_paste_typer) * 1000
        max_time = (length / super_typer) * 1000
        return round(min_time), round(max_time)
    except Exception:
        logger.error("Unable to get dynamic WhatsApp presence (EVO delay)")
