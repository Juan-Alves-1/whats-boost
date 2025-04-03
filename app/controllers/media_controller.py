from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.send_media import send_group_media_messages

router = APIRouter()

class BulkMediaRequest(BaseModel):
    group_ids: List[str]
    caption: str
    media_url: str
    file_name: str
    initial_delay: int
    subsequent_delay: int
    mediatype: str
    mimetype: str

@router.post("/media")
def send_bulk_media(payload: BulkMediaRequest):
    try:
        results = send_group_media_messages(
            group_ids=payload.group_ids,
            caption=payload.caption,
            media_url=payload.media_url,
            file_name=payload.file_name,
            initial_delay=payload.initial_delay,
            subsequent_delay=payload.subsequent_delay,
            mediatype=payload.mediatype,
            mimetype=payload.mimetype
        )
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
