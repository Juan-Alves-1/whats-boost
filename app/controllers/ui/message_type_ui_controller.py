from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from app.dependencies.auth import auth_required
from app.config.templates import templates

router = APIRouter()

@router.get("/choose", response_class=HTMLResponse)
async def show_choose_type(request: Request, user=Depends(auth_required)):
    return templates.TemplateResponse("choose_message_type.html", context= {
        "request": request,
        "text_form": request.url_for("show_text_form"),
        "media_form": request.url_for("show_media_form")
    })

