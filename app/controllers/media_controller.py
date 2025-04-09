from fastapi import APIRouter, HTTPException, Depends, Request, Form
from pydantic import BaseModel
from typing import List
from fastapi.responses import HTMLResponse
from app.services.send_media import send_group_media_messages
from app.dependencies.auth import auth_required
from app.config.group_map import GROUP_IDS
from app.config.templates import templates

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

@router.get("/media", response_class=HTMLResponse)
async def show_media_form(request: Request, user=Depends(auth_required)):
    return templates.TemplateResponse("media_message.html", {"request": request})

@router.post("/media")
async def send_bulk_media_ui(request: Request , message_text: str = Form(...), image_url: str = Form(...), image_name: str = Form(...), user=Depends(auth_required)):
    try:
        group_ids = list(GROUP_IDS.values()) # Gets all test group IDs
        results = send_group_media_messages(
            group_ids=group_ids,
            caption=message_text,
            media_url=image_url,
            file_name=image_name
        )
        return templates.TemplateResponse("media_message.html", {
            "request": request,
            "form_action": request.url_for("send_bulk_media_ui"), # It dynamically constructs the URL path
            "success": True,  # Tells the frontend when to fire the alert
            "Result": results # Double-check !!!!!!!!!!!!!!!!!!!!!!!
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
