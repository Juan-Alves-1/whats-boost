from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.config.settings import settings
from app.config.templates import templates

router = APIRouter()

# Set as a public landing page for unauthenticated users
@router.get("/", response_class=HTMLResponse)
async def show_homepage(request: Request):
    user = request.session.get("user")
    if not user or user.get("email") not in settings.ALLOWED_EMAILS:
        return templates.TemplateResponse("index.html", context= {
            "request": request,
            "login_url": request.url_for("login")
        })

    return RedirectResponse(request.url_for("show_choose_type"), status_code=301)
