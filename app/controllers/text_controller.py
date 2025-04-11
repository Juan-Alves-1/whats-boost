from fastapi import APIRouter, HTTPException, Depends, Request, Form
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import HTMLResponse, RedirectResponse
from app.services.send_text import send_group_text_messages
from app.dependencies.auth import auth_required
from app.config.group_map import GROUP_IDS
from app.config.templates import templates
import asyncio

router = APIRouter()

class BulkTextRequest(BaseModel):
    group_ids: List[str]
    message_text: str
    initial_delay: Optional[int] = 10000
    subsequent_delay: Optional[int] = 70000

@router.get("/text", response_class=HTMLResponse)
async def show_text_form(request: Request, user=Depends(auth_required)):
    sent = request.query_params.get("sent") == "true"
    return templates.TemplateResponse("text_message.html", {
        "request": request,
        "form_action": request.url_for("send_bulk_text_ui"),
        "success": sent,  # flag to show confirmation
        "Result": "The messages were scheduled!"
    })

@router.post("/text", response_class=HTMLResponse)
async def send_bulk_text_ui(
    request: Request,
    message_text: str = Form(...),
    user=Depends(auth_required)
):
    try:
        group_ids = list(GROUP_IDS.values()) # Gets all test group IDs
        
        # Quick solution to launch the batch in the background
        asyncio.create_task(send_group_text_messages(group_ids, message_text))

        # Redirect to GET with query param so user doesn't re-submit 
        # request.url_for(...) returns a Starlette URL object, not a plain string
        redirect_url = str(request.url_for("show_text_form")) + "?sent=true"
        return RedirectResponse(url=redirect_url, status_code=303)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
