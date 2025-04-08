from fastapi import APIRouter, HTTPException, Depends, Request, Form
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.send_text import send_group_text_messages
from app.dependencies.auth import auth_required
from app.config.group_map import GROUP_IDS

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

class BulkTextRequest(BaseModel):
    group_ids: List[str]
    message_text: str
    initial_delay: Optional[int] = 10000
    subsequent_delay: Optional[int] = 70000

@router.get("/text", response_class=HTMLResponse)
async def show_text_form(request: Request, user=Depends(auth_required)):
    return templates.TemplateResponse("text_message.html", {"request": request})

@router.post("/text", response_class=HTMLResponse)
async def send_bulk_text_ui(
    request: Request,
    message_text: str = Form(...),
    user=Depends(auth_required)
):
    try:
        group_ids = list(GROUP_IDS.values()) # Gets all test group IDs
        results = send_group_text_messages(
            group_ids=group_ids,
            message_text=message_text,
        )
        return templates.TemplateResponse("text_message.html", {
            "request": request,
            "form_action": request.url_for("send_bulk_text_ui") # It dynamically constructs the URL path
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
