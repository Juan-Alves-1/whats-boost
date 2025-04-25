from datetime import datetime

# Format timestamp for logging readability
def format_timestamp(ts: str) -> str:
    try:
        return datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return "Invalid timestamp"
