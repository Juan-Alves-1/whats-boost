import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.config.settings import settings,Env
from app.utils.logger import logger

# Route Controllers
from app.controllers import  auth_controller
from app.controllers.ui import homepage_controller, message_type_ui_controller, text_ui_controller, media_ui_controller
from app.controllers.api import link_api_controller, text_api_controller, media_api_controller, image_up_api_controller, image_up_logo_api_controller

app = FastAPI(title="WhatsApp Boost Tool")

# 🛡️ Middleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY, max_age=604800, https_only=False) # Secure cookie-based sessions (7 days)

# 🔐 Authentication Routes
app.include_router(auth_controller.router, tags=["Auth"])

# 🌐 UI Routes (Jinja2)
app.include_router(homepage_controller.router, tags=["UI"])  # Homepage
app.include_router(message_type_ui_controller.router, tags=["UI"]) # Show message options
app.include_router(text_ui_controller.router, tags=["UI"]) # Show form for text
app.include_router(media_ui_controller.router, tags=["UI"]) # Show form for media

# 🚀 API Routes (JSON)
app.include_router(text_api_controller.router, tags=["API", "Messages"]) # Fire text messages
app.include_router(media_api_controller.router, tags=["API", "Messages"]) # Fire media messages
app.include_router(link_api_controller.router, tags=["API", "Messages"])

app.include_router(image_up_api_controller.router, tags=["API", "Images"]) # Upload image to the provider
app.include_router(image_up_logo_api_controller.router, tags=["API", "Images"]) # Upload image to the provider

def main():
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENV == Env.DEVELOPMENT if True else False,
    )

if __name__ == "__main__":
    logger.info("🚀 WhatsBoost starting...")

    main()
