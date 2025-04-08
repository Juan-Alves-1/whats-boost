from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.config.settings import settings
from app.controllers import text_controller, media_controller, auth_controller

app = FastAPI(title="WhatsApp Boost Tool")

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY, https_only=False)

app.include_router(auth_controller.router, tags=["Auth"])
# Include text_controller routes under a specific path
app.include_router(text_controller.router, prefix="/send", tags=["Send Actions"])
app.include_router(media_controller.router, prefix="/send", tags=["Send Actions"])

@app.get("/")
def read_root():
    return {"message": "WhatsApp Boost Tool API is running."}
