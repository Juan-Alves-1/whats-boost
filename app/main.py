from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.config.settings import settings

# Route Controllers
from app.controllers import  auth_controller
from app.controllers.ui import homepage_controller, text_ui_controller, media_ui_controller
from app.controllers.api import text_api_controller, media_api_controller

app = FastAPI(title="WhatsApp Boost Tool")

# 🛡️ Middleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY, max_age=604800, https_only=False) # Add session middleware

# 🔐 Authentication Routes
app.include_router(auth_controller.router, tags=["Auth"])

# 🌐 UI Routes (Jinja2)
app.include_router(homepage_controller.router, tags=["Home"])  # Homepage
app.include_router(text_ui_controller.router, tags=["UI"]) # Show form for text
app.include_router(media_ui_controller.router, tags=["UI"]) # Show form for media

# 🚀 API Routes (JSON)
app.include_router(text_api_controller.router, tags=["API"]) # Fire text messages
app.include_router(media_api_controller.router, tags=["API"]) # Fire media messages

