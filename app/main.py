from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.config.settings import settings
from app.utils.http_client import shared_http_client
from app.utils.logger import logger

# Route Controllers
from app.controllers import  auth_controller
from app.controllers.ui import homepage_controller, message_type_ui_controller, text_ui_controller, media_ui_controller
from app.controllers.api import text_api_controller, media_api_controller, user_api_controller, image_up_api_controller

@asynccontextmanager
async def lifespan(app: FastAPI):
    # App startup
    logger.info("🚀 WhatsBoost starting...")
    yield
    # App shutdown 
    #logger.info("🛑 WhatsBoost shutting down. Closing HTTP client...")
    #await shared_http_client.aclose()

app = FastAPI(title="WhatsApp Boost Tool", lifespan=lifespan)

# 🛡️ Middleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY, max_age=604800, https_only=False) # Secure cookie-based sessions (7 days)

# 🔐 Authentication Routes
app.include_router(auth_controller.router, tags=["Auth"])

# 🌐 UI Routes (Jinja2)
app.include_router(homepage_controller.router, tags=["Home"])  # Homepage
app.include_router(message_type_ui_controller.router, tags=["UI"]) # Show message options
app.include_router(text_ui_controller.router, tags=["UI"]) # Show form for text
app.include_router(media_ui_controller.router, tags=["UI"]) # Show form for media

# 🚀 API Routes (JSON)
app.include_router(text_api_controller.router, tags=["API"]) # Fire text messages
app.include_router(media_api_controller.router, tags=["API"]) # Fire media messages
app.include_router(user_api_controller.router, tags=["Users"]) # CRUD operations for user

app.include_router(image_up_api_controller.router, tags=["Image Upload"]) # Upload image to the provider

