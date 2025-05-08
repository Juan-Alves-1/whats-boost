from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.responses import RedirectResponse
from app.dependencies.auth import auth_required
from app.schemas.message import bulk_media_payload
from app.config.group_map import GROUP_IDS
from app.utils.media_validation import is_image_url
from app.tasks.batch_queue import enqueue_user_media_batch
from app.utils.logger import logger

import asyncio

router = APIRouter()

@router.post("/api/v1/messages/media", name="send_media_ui")
async def send_bulk_media_ui(request: Request , message_text: str = Form(...), image_url: str = Form(...), user=Depends(auth_required)):
    try:
        # Build + validate structured payload using Pydantic model
        payload = bulk_media_payload(
            group_ids = list(GROUP_IDS.values()), # Gets all test group IDs  
            caption=message_text,
            media_url=image_url 
        )

        payload_dict = payload.model_dump()
        payload_dict["user_email"] = user["email"]

        # Validate media_url before creating tasks
        if not is_image_url(payload.media_url):
            raise HTTPException(status_code=400, detail="Provided media_url is not an image.")
            
        # Enqueue task via Celery for queue management
        enqueue_user_media_batch.delay(payload_dict)
        
        # Redirect user to prevent resubmission
        redirect_url = str(request.url_for("show_media_form")) + "?sent=true" # request.url_for(...) returns a Starlette URL object, not a plain string
        return RedirectResponse(url=redirect_url, status_code=303)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
