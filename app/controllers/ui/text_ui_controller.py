from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse
from app.dependencies.auth import auth_required
from app.config.templates import templates

router = APIRouter()

@router.get("/send-text", response_class=HTMLResponse, name="show_text_form")
async def show_text_form(request: Request, user=Depends(auth_required)):
    sent = request.query_params.get("sent") == "true"
    return templates.TemplateResponse("text_message.html", {
        "request": request,
        "form_action": request.url_for("send_text_ui"),
        "success": sent,  # flag to show confirmation
        "Result": "The messages were scheduled!"
    })


