from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.config.settings import settings
from app.controllers import  auth_controller
from app.controllers.ui import text_ui_controller, media_ui_controller
from app.controllers.api import text_api_controller, media_api_controller

app = FastAPI(title="WhatsApp Boost Tool")

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY, https_only=False) # Add session middleware

app.include_router(auth_controller.router, tags=["Auth"])

app.include_router(text_ui_controller.router, tags=["UI"])
app.include_router(media_ui_controller.router, tags=["UI"])

app.include_router(text_api_controller.router, tags=["API"])
app.include_router(media_api_controller.router, tags=["API"])


@app.get("/")
def root():
    return {"message": "WhatsApp Boost Tool is running."}
