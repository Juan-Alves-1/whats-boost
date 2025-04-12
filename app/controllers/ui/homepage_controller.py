from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.config.templates import templates

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def show_homepage(request: Request):
    return templates.TemplateResponse("index.html", context= {"request": request})
