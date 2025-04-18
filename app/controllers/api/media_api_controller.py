from fastapi import APIRouter, HTTPException, Depends, Request, Form
from pydantic import BaseModel
from typing import List
from fastapi.responses import RedirectResponse
from app.services.send_media import send_group_media_messages
from app.dependencies.auth import auth_required
from app.config.group_map import GROUP_IDS
import asyncio

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

@router.post("/api/v1/messages/media", name="send_media_ui")
async def send_bulk_media_ui(request: Request , message_text: str = Form(...), image_url: str = Form(...), user=Depends(auth_required)):
    try:
        group_ids = list(GROUP_IDS.values()) # Gets all test group IDs
        # Quick solution to launch the batch in the background
        asyncio.create_task(send_group_media_messages(
            group_ids=group_ids,
            caption=message_text,
            media_url=image_url
        ))
        # Redirect to GET with query param so user doesn't re-submit 
        # request.url_for(...) returns a Starlette URL object, not a plain string
        redirect_url = str(request.url_for("show_media_form")) + "?sent=true"
        return RedirectResponse(url=redirect_url, status_code=303)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
