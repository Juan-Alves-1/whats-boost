from fastapi import FastAPI
from app.config.settings import settings
from app.controllers import text_controller, media_controller

app = FastAPI(title="WhatsApp Boost Tool")

# Include text_controller routes under a specific path
app.include_router(text_controller.router, prefix="/send", tags=["Send Actions"])
app.include_router(media_controller.router, prefix="/send", tags=["Send Actions"])

@app.get("/")
def read_root():
    return {"message": "WhatsApp Boost Tool API is running."}
