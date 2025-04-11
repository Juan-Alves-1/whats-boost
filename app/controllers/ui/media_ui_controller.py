from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.services.send_media import send_group_media_messages
from app.dependencies.auth import auth_required
from app.config.templates import templates

router = APIRouter()

@router.get("/send-media", response_class=HTMLResponse, name="show_media_form")
async def show_media_form(request: Request, user=Depends(auth_required)):
    sent = request.query_params.get("sent") == "true"
    return templates.TemplateResponse("media_message.html", {
        "request": request,
        "form_action": request.url_for("send_media_ui"),
        "success": sent,  # flag to show confirmation
        "Result": "The messages were scheduled!"
    })

